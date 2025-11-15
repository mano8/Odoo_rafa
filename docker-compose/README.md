# Odoo Docker Compose

A production-ready Docker Compose stack for **Odoo 18**, **PostgreSQL 13**, **Traefik v3**, the **FastAPI `hw_proxy_service`**, and the **`hw_status`** service.

* **Online mode**: pull images and dependencies from the Internet (default).
* **Offline mode**: run fully air-gapped after pre-caching images and Python wheels.

---

## Table of contents

1. [Requirements](#requirements)
2. [Online mode (recommended)](#online-mode-recommended)

   * [POS printer configuration for `hw_proxy_service`](#pos-printer-configuration-for-hw_proxy_service)
   * [Set up `.env` files](#set-up-env-file)
   * [Set up Odoo config (`odoo.conf`)](#set-up-odoo-config-file)
   * [Set correct owners for volumes (Linux/Unix)](#on-unix-set-correct-owners-for-docker-volumes)
   * [Build & run containers](#build-containers)
   * [Initialize the database](#init-data-base-in-odoo-container)
3. [Offline mode](#offline-mode)
4. [Auto-run the stack with systemd](#2-auto-run-docker-compose-containers)
5. [Container logs (journald)](#3-containers-logs)

---

## Requirements

* Docker ≥ 24, Docker Compose v2
* Linux (or Windows with WSL2)
* For printing: access to the host **serial/USB** device and **udev** permissions
* Traefik local TLS certificates (if you expose HTTPS locally)

### POS printer configuration for `hw_proxy_service`

By default Odoo expects an **IoT Box** or **Epson** printer.
In this stack, the **FastAPI `hw_proxy_service`** bridges Odoo with your **POS printer**. It needs:

* Access to the **serial port** (`/dev/ttyACM*` or `/dev/ttyUSB*`)
* Correct **serial parameters** (baudrate, parity, etc.)
* A **udev** rule to grant the service user access to the device

See:

* `../fiesta_pos/hw_proxy/hw_proxy/README.md` — udev & serial setup
* `../fiesta_pos/hw_proxy/hw_proxy/core/supported_devices.py` — printer profiles
* `../fiesta_pos/hw_proxy/hw_proxy/en.example.txt` — `.env` example for the service

---

## Online mode (recommended)

### Set up `.env` file

Copy the **compose** environment file:

```bash
cp ./env.example.txt ./.env
# Update env values
nano .env
```

Copy the **hw_proxy** environment file:

```bash
cp ./hw_proxy.env.example.txt ./hw_proxy.env
# Update hw_proxy env values
nano hw_proxy.env
```

> Ensure DB variables match your setup (defaults from this repo):
> `DB_HOST=fiesta_db`, `DB_DATABASE=odoo`, `DB_USER=odoo`, `DB_PASSWORD=changethis`

### Set up Odoo config file

Add the same DB connection as in `.env`:

```bash
nano ./odoo/config/odoo.conf
```

Example minimal block:

```ini
[options]
db_host = fiesta_db
db_name = odoo
db_user = odoo
db_password = changethis
# Optional:
# log_level = info
# workers = 2
```

### On Unix: Set correct owners for docker volumes

Container processes run with the **container user’s UID/GID**.
Ensure volume directories on the host are owned by matching IDs to avoid permission issues.

Inspect Odoo’s user inside the official image:

```bash
sudo docker run --rm odoo:18.0 id odoo
# Usually:
# uid=100(odoo) gid=101(odoo) groups=101(odoo)
```

Check host UID/GID collisions (adjust as needed):

```bash
id -un -- 100 || true
getent group 101 || true
```

Fix ownership of your mounted Odoo directories:

```bash
sudo chown -R 100:101 ./odoo
```

---

## Build containers

Build and start the stack:

```bash
sudo docker compose up --build --remove-orphans
```

> First run may take longer (images, dependencies, DB init checks).

### Init data base in Oddo container

Manual DB initialization (optional):

```bash
sudo docker compose run --rm fiesta_odoo bash
```

Inside the container:

```bash
odoo --init base \
  --database odoo \
  --stop-after-init \
  --db_host=fiesta_db \
  --db_user=odoo \
  --db_password=changethis \
  --without-demo=True

exit
```

Then run the stack normally:

```bash
sudo docker compose up --build --remove-orphans
```

---

## Offline mode

If running **without Internet**, ensure everything is cached locally first:

1. **Pre-pull & save** required images (Traefik, Postgres, Odoo)
2. **Pre-build & cache** `hw_proxy_service` base image and **wheelhouse** dependencies
3. Use **offline Dockerfiles** and tar-loaded images

### Pre-pull & save your base images

```bash
sudo mkdir -p /opt/Odoo_rafa/docker_offline
cd /opt/Odoo_rafa/docker_offline

sudo docker pull traefik:v3.4.0
sudo docker pull postgres:13.21-alpine3.20
sudo docker pull odoo:18.0

sudo docker save traefik:v3.4.0 -o traefik_v3.4.0.tar
sudo docker save postgres:13.21-alpine3.20 -o postgres_13.21-alpine3.20.tar
sudo docker save odoo:18.0 -o odoo_18.0.tar

# Later, on the offline host:
sudo docker load -i traefik_v3.4.0.tar
sudo docker load -i postgres_13.21-alpine3.20.tar
sudo docker load -i odoo_18.0.tar
```

### `hw_proxy_service` container (offline)

1. Build & save base image:

    ```bash
    # inside /opt/Odoo_rafa/hw_proxy (where Dockerfile.fat lives)
    sudo docker build -f Dockerfile.fat -t python-3.11-fat:latest .
    sudo docker save python-3.11-fat:latest -o python-3.11-fat.tar

    # later, offline:
    sudo docker load -i python-3.11-fat.tar
    ```

2. Cache Python packages:

    ```bash
    cd /opt/Odoo_rafa/hw_proxy

    mkdir -p wheelhouse wheelhouse_dev
    pip download --dest wheelhouse     -r hw_proxy/requirements-docker.txt
    pip download --dest wheelhouse_dev -r hw_proxy/requirements-docker-dev.txt
    ```

3. Offline Dockerfiles available:

    * `../hw_proxy/hw_proxy/Dockerfile.offline` (production)
    * `../hw_proxy/hw_proxy/Dockerfile.offline-dev` (development)

Ensure they point to your **wheelhouse** and **local base image**.

---

## 2. Auto run docker compose containers

> **Warning**
> This systemd unit only **runs** containers; you must **build them first**:

```bash
sudo docker compose build
```

> **Important**
> Use systemd service type **`oneshot`** and set **`restart: unless-stopped`** on every service in `docker-compose.yml`.

Install the service:

```bash
sudo cp ../services/odoo_server/odoo-pos.service /etc/systemd/system/odoo-pos.service
```

Enable & start:

```bash
sudo systemctl enable odoo-pos.service
sudo systemctl daemon-reload
sudo systemctl start odoo-pos.service
```

Check status:

```bash
sudo systemctl status odoo-pos.service
sudo journalctl -xeu odoo-pos.service
```

---

## 3. Containers logs

### Docker-level log driver

Add this to any service that must log via systemd:

```yaml
logging:
  driver: "journald"
```

Check a container’s log driver:

```bash
sudo docker inspect -f '{{ .HostConfig.LogConfig.Type }}' odoo_dev-fiesta_odoo-1
```

### View logs

List container names:

```bash
sudo docker ps --format '{{.Names}}'
```

Example:

```bash
odoo_dev-fiesta_odoo-1
odoo_dev-traefik-1
odoo_dev-fiesta_db-1
odoo_dev-hw_proxy_service-1
```

Follow logs with **systemd/journald**:

```bash
sudo journalctl -f CONTAINER_NAME=odoo_dev-fiesta_odoo-1
# full messages:
sudo journalctl -f CONTAINER_NAME=odoo_dev-fiesta_odoo-1 -all
```

Or via Docker:

```bash
sudo docker logs -f odoo_dev-fiesta_odoo-1
```

> For journald tuning (retention, size limits), see `../docker/README.md` (journald section).

---

### Related docs in this repo

* [**Docker hardening (mTLS, userns-remap, journald):**](../docker/README.md)
* [**Manual mTLS certificate generation:**](../docker/docker_manual_certs.md)
* [**hw_proxy setup:**](../fiesta_pos/hw_proxy/README.md)
