# `hw_proxy` service

This must run on host machine dirrectly, this app can:

- control PP6800 printer and cachdrawer on ttyACM0 port
- ShutDown and Reboot system
- Get current connected devices to host machine
- Get current ttyACM0 serial configuration
- Get journalctl logs from docker and all containers in docker compose
- Save oddo postgres database on disk, zip and dowload
- Restart selected container
- Run and build docker compose

## Configuration

### Add User and Groups for `hw_proxy` service and `ttyACM0`
- Create new user 

```bash
sudo adduser --disabled-password --gecos "" hw_user
```

- create new group

```bash
sudo groupadd pp6800
sudo usermod -aG pp6800 hw_user
```

### Configure udev rules

- Config ttyACM0 permissions

```bash
sudo nano /etc/udev/rules.d/99-escpos.rules
```

Paste this content

```text
KERNEL=="ttyACM0", MODE="0660", GROUP="pp6800"
```

Reload Udev

```bash
sudo udevadm control --reload
sudo udevadm trigger
```

verrify

```bash
ls -alt /dev/ttyACM0
# crw-rw---- 1 root pp6800 166, 0 jun  1 16:25 /dev/ttyACM0
```