# ⚙️ `hw_proxy` Service

The **`hw_proxy`** service runs **directly on the host machine**, providing a secure bridge between **Odoo POS** and **local hardware** such as printers, cash drawers, and system controls.

It is **not containerized** — it interacts with physical devices and communicates with Odoo (running in Docker) over HTTPS through **Traefik** (`/hw_proxy` route).

---

## 🧭 Overview

This service exposes hardware and system control endpoints used by the **Odoo Local POS Stack**.

### 🧾 Capabilities

* 🖨️ Control **ESC/POS-compatible printers** (e.g., Posiflex PP6800) and **cash drawers**.
* 🔌 Manage host power operations:

  * **Shutdown** or **Reboot** the host system.
* 🔍 Enumerate **connected hardware devices** (USB, serial, etc.).
* ⚙️ Retrieve **serial configuration** for the printer port (e.g., `/dev/ttyACM0`).
* 📜 Collect **Docker and system logs** (`journalctl`) for diagnostics.
* 💾 Perform **Odoo PostgreSQL backups**:

  * Dumps the database, compresses it as ZIP, and serves it for download.
* 🔁 **Restart containers** or **rebuild the Docker stack** via API commands.

---

## 🧩 Integration

In the main stack, **Traefik** proxies HTTPS requests from Odoo to the host’s `hw_proxy` service:

```bash
https://traefik-client.local:9001/hw_proxy  →  http://192.168.1.146:9002
```

This setup allows Odoo to send printing or control commands securely to the host while maintaining direct hardware access.

---

## ⚙️ Host Configuration

### 1️⃣ Create a Dedicated User and Group

The service should **never** run as `root`.
Create a restricted user and group for printer access.

```bash
sudo adduser --disabled-password --gecos "" hw_user
sudo groupadd printer
sudo usermod -aG printer hw_user
```

> You may name the group as you prefer (`printer`, `pp6800`, etc.) — just ensure the same name is used in your udev rule.

---

### 2️⃣ Identify Your POS Printer Device

Before setting permissions, determine which `/dev/tty*` device your printer is using.

#### 🔍 Detect your printer after plugging it in

Run one of these commands right after connecting the printer:

```bash
dmesg | grep tty
```

Example output:

```bash
[ 1256.432187] cdc_acm 1-1.2:1.0: ttyACM0: USB ACM device
```

List all serial/USB devices:

```bash
ls /dev/tty*
```

Get detailed information:

```bash
sudo udevadm info -q path -n /dev/ttyACM0
sudo udevadm info -a -n /dev/ttyACM0 | grep 'ATTRS{product}'
```

Check connected USB devices:

```bash
lsusb
```

Example:

```bash
Bus 001 Device 005: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
```

> 💡 On some systems your printer may appear as `/dev/ttyUSB0`, `/dev/ttyACM1`, or another name.
> Adjust all udev rules and service files accordingly.

---

### 3️⃣ Configure udev Rules

Create a persistent rule to ensure the printer port always has the right permissions.

1. Create the rule file:

   ```bash
   sudo nano /etc/udev/rules.d/99-escpos.rules
   ```

2. Add the following content (update the port and group if needed):

   ```text
   KERNEL=="ttyACM0", MODE="0660", GROUP="printer"
   ```

3. Reload and apply:

   ```bash
   sudo udevadm control --reload
   sudo udevadm trigger
   ```

4. Verify:

   ```bash
   ls -l /dev/ttyACM0
   # crw-rw---- 1 root printer 166, 0 Jun  1 16:25 /dev/ttyACM0
   ```

---

### 4️⃣ Configure and Run the Services

By default, the app listens on **port 9002** and is proxied by Traefik.

> The examples below assume the repository is cloned under `/opt/Odoo_rafa`.

#### 🧩 `hw_proxy` Service

Install the predefined systemd unit file:

```bash
sudo cp /opt/Odoo_rafa/services/odoo_server/hw_proxy.service /etc/systemd/system/hw_proxy.service
```

> [View hw_proxy.service](https://github.com/mano8/Odoo_rafa/blob/main/services/odoo_server/hw_proxy.service)

Enable and start it:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable hw_proxy.service
sudo systemctl daemon-reload
sudo systemctl start hw_proxy.service
```

Check status and logs:

```bash
sudo systemctl status hw_proxy.service
sudo journalctl -xeu hw_proxy.service
```

---

#### ⚙️ Auto-Configure Serial Port for the POS Printer

By default, serial/USB ports such as `/dev/ttyACM0` are set to **9600 baud**.
This helper service automatically configures your printer port with the correct parameters (e.g., 115200 baud, 8-N-1).

Create `/etc/systemd/system/serial-config.service`:

```ini
[Unit]
Description=Configure POS Serial Port
After=dev-ttyACM0.device
Wants=dev-ttyACM0.device

[Service]
Type=oneshot
ExecStart=/usr/bin/stty -F /dev/ttyACM0 115200 cs8 -cstopb -parenb -crtscts -echo
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

> [View serial-config.service](https://github.com/mano8/Odoo_rafa/blob/main/services/odoo_server/serial-config.service)
> Replace `ttyACM0` with your actual printer port if different.

Enable and start:

```bash
sudo systemctl enable serial-config.service
sudo systemctl daemon-reload
sudo systemctl start serial-config.service
```

Check status:

```bash
sudo systemctl status serial-config.service
sudo journalctl -xeu serial-config.service
```

---

## 🖨️ Printer & Environment Configuration

### 📁 Directory Structure (exact paths)

```bash
fiesta_pos/
└─ hw_proxy/
   └─ hw_proxy/
      ├─ core/
      │  └─ supported_devices.py      ← configure printer models & defaults here
      ├─ app/
      │  ├─ static/                   ← static assets (STATIC_BASE_PATH)
      │  └─ templates/                ← Jinja templates (TEMPLATES_BASE_PATH)
      ├─ en.example.txt               ← example environment file → copy to .env
      └─ ...                          ← FastAPI app and modules
```

---

### 🔧 Configure Your Printer

Edit:

```bash
fiesta_pos/hw_proxy/hw_proxy/core/supported_devices.py
```

Current example configuration:

```python
device_list = [
    {
        'vendor': "0x0d3a",
        'product': "0x0368",
        'name': 'Posiflex PP6800',
        'key': 'PP6800',
        'type': DeviceType.PRINTER,
        'port_type': DevicePortType.SERIAL,
        'conf': {
            "devfile": "/dev/ttyACM0",
            "baudrate": 115200,
            "bytesize": 8,
            "parity": 'N',
            "stopbits": 1,
            "timeout": 2,
            "dsrdtr": False,
            "profile": "TM-L90"
        },
        'image_conf': {
            "impl": "bitImageColumn"
        }
    },
]
```

**Field descriptions:**

| Field                | Description                                                 |
| -------------------- | ----------------------------------------------------------- |
| `vendor` / `product` | USB vendor/product IDs (from `lsusb`).                      |
| `name`               | Human-readable model name.                                  |
| `key`                | Unique printer key; must match `.env → PRINTER_KEY`.        |
| `type`               | Always `DeviceType.PRINTER` for printers.                   |
| `port_type`          | Usually `DevicePortType.SERIAL` for USB/serial devices.     |
| `conf.devfile`       | Actual serial device (e.g. `/dev/ttyACM0`, `/dev/ttyUSB0`). |
| `conf.baudrate`      | Communication speed (e.g. 9600 or 115200).                  |
| `profile`            | Driver profile name (`TM-L90`, `EPSON`, etc.).              |
| `image_conf`         | Bitmap rendering method for image printing.                 |

If you use another printer model, duplicate this entry and modify:

* `vendor`, `product`, `name`, `key`
* the `devfile` and serial parameters to match your hardware.

---

### ⚙️ Configure the Environment File

Create `.env` from the provided example:

```bash
cp fiesta_pos/hw_proxy/hw_proxy/en.example.txt fiesta_pos/hw_proxy/hw_proxy/.env
nano fiesta_pos/hw_proxy/hw_proxy/.env
```

Main example content:

```ini
DOMAIN="localhost"
ENVIRONMENT="local"

API_PREFIX="/hw_proxy"
SET_OPEN_API=true
SET_DOCS=true
SET_REDOC=true

PROJECT_NAME="OdooHwProxy"
STACK_NAME="full-stack-oddo-hw-proxy"

STATIC_BASE_PATH="/opt/fiesta-pos/hw_proxy/hw_proxy/app/static"
TEMPLATES_BASE_PATH="/opt/fiesta-pos/hw_proxy/hw_proxy/app/templates"

BACKEND_HOST="http://192.168.1.146:9000"
FRONTEND_HOST="http://192.168.1.146:9001"
BACKEND_CORS_ORIGINS="http://192.168.1.146:9000,https://192.168.1.146:9000,http://192.168.1.146:9001,https://192.168.1.146:9001"
SECRET_KEY="changethis"

# Must match the key defined in supported_devices.py
PRINTER_KEY="PP6800"

LOG_LEVEL="Debug"
```

**Check these values carefully:**

* `PRINTER_KEY` → must match the device key (`PP6800`, etc.).
* `DOMAIN`, `BACKEND_HOST`, `FRONTEND_HOST` → your actual IP or hostname.
* `STATIC_BASE_PATH` / `TEMPLATES_BASE_PATH` → correct for your deployment path.
* `SECRET_KEY` → replace `"changethis"`.

---

## 🧪 Testing

Verify connectivity through Traefik:

```bash
curl https://traefik-client.local:9001/hw_proxy/health
```

Expected response:

```json
{"status":"ok","printer":"connected"}
```

Trigger a test print:

```bash
curl -X POST https://traefik-client.local:9001/hw_proxy/test_print
```

A small test receipt should print successfully.

---

## 🔒 Security Best Practices

* Run as **non-root** (`hw_user` in the printer group only).
* Restrict Traefik exposure to your **local network**.
* Protect access to critical endpoints (`/reboot`, `/shutdown`, `/backup`).
* Periodically audit `journalctl` logs and stored backups.
* Keep Python and dependencies updated.

---

## 👨‍💻 Developer

Developed and maintained by **Eli Serra**
Part of the [Odoo Local POS Stack](../README.md)
Built with **FastAPI**, **Uvicorn**, and **Python 3.11 +**

---

## 📜 License

Licensed under the **Apache License 2.0**.
See the [LICENSE](../LICENSE) file for full terms.
