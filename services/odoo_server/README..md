# Odoo Server services

## 0. hw_proxy service

- Add service to `systemd`

```bash
sudo cp /opt/Odoo_rafa/services/odoo_server/hw_proxy.service /etc/systemd/system/hw_proxy.service
```

- Enable it

```bash
sudo systemctl daemon-reexec
sudo systemctl enable hw_proxy.service
sudo systemctl daemon-reload
sudo systemctl start hw_proxy.service
```

- Check status

```bash
sudo systemctl status hw_proxy.service
sudo journalctl -xeu hw_proxy.service
```

## 1. Auto configure ttyACM0 port for PP6800 printer

By default ttyACM0 is configure with baud od 9600.
This Service configure ttyACM0 with correct parameters for PP6800 printer

### Install and activate

- Add service to `systemd`

```bash
sudo cp services/odoo_server/serial-config.service /etc/systemd/system/serial-config.service
```

- Enable it

```bash
sudo systemctl enable serial-config.service
sudo systemctl daemon-reload
sudo systemctl start serial-config.service
```

- Check status

```bash
sudo systemctl status serial-config.service
sudo journalctl -xeu serial-config.service
```

## 2. Auto run docker compose containers

**Warnin**  
This service only run containers, you must pre build with

```bash
sudo docker compose build
```

**Important**  
Need to use `oneshot` systemd service type.
And all containers must have:

```yml
    restart: unless-stopped
```

- Add service to `systemd`

```bash
sudo cp /opt/Odoo_rafa/services/odoo_server/odoo-pos.service /etc/systemd/system/odoo-pos.service
```


- Enable it

```bash
sudo systemctl enable odoo-pos.service
sudo systemctl daemon-reload
sudo systemctl start odoo-pos.service
```

- Check status

```bash
sudo systemctl status odoo-pos.service
sudo journalctl -xeu odoo-pos.service
```

## 3. Containers logs

### Docker-Level Logs

- Add this to all container who needs logs.

```yml
    logging:
      driver: "journald"
```

- to check docker logs driver

```bash
sudo docker inspect -f '{{ .HostConfig.LogConfig.Type }}' odoo_dev-fiesta_odoo-1
```

#### View logs

- first need to identify container names

```bash
sudo docker ps --format '{{.Names}}'
```

- Get somthing as 

```text
odoo_dev-fiesta_odoo-1
odoo_dev-traefik-1
odoo_dev-fiesta_db-1
odoo_dev-hw_proxy_service-1
```

- to view logs from systemd

```bash
sudo journalctl -f CONTAINER_NAME=odoo_dev-fiesta_odoo-1
```

- to view complete message logs from systemd

```bash
sudo journalctl -f CONTAINER_NAME=odoo_dev-fiesta_odoo-1 -all
```

- to view logs directly in docker

```bash
sudo docker logs -f odoo_dev-fiesta_odoo-1
```


### Configure journald 

- create `/etc/systemd/journald.conf.d/00-docker.conf`

```bash
sudo nano /etc/systemd/journald.conf.d/00-docker.conf
```

- And add above content

```ini
[Journal]
# Limit total disk space taken by all journal files
SystemMaxUse=1G
# Always leave at least this much free space on the filesystem
SystemKeepFree=100M

# Cap individual journal files to 100 MiB each
SystemMaxFileSize=100M
# Keep at most 10 archived journal files
SystemMaxFiles=10

# Runtime (volatile) journals in /run/log/journal
RuntimeMaxUse=200M
RuntimeKeepFree=50M
RuntimeMaxFileSize=50M
RuntimeMaxFiles=5

# Optionally expire entries older than 2 weeks
MaxRetentionSec=2week

# Compress archived journal files
Compress=yes
```

- `SystemMaxUse=` controls aggregate size for persistent logs (typically in `/var/log/journal`)
- `SystemMaxFileSize=` sets how big each file grows before rotating
- `SystemMaxFiles=` limits number of archived files
- The `Runtime*` settings apply to volatile logs in `/run/log/journal`
- `MaxRetentionSec=` and `MaxFileSec=` (not shown) can govern time-based retention.

- After ediiting reload with

```bash
sudo systemctl restart systemd-journald
```

- Can see full config with

```bash
sudo systemd-analyze cat-config systemd/journald.conf
```
