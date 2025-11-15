# 🧾 Odoo Rafa's Local POS Stack

**Self-contained local Odoo 18 ecosystem** integrating a **FastAPI-based hardware status dashboard**, optional **external POS printer proxy**, and **Traefik with locally trusted SSL certificates** — extended by a **custom Odoo POS add-on** for per-unit ticket printing.

> A ready-to-run Odoo 18 Point of Sale environment designed for local, secure, and hardware-integrated deployments.
> Eliminates the need for Odoo IoT Box while offering full HTTPS security, test printing, and local monitoring tools.

[License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)

---

## ✨ Overview

This project provides a **local Odoo POS server** with:

| Component                        | Description                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------- |
| 🧱 **Odoo 18.0**                 | Main ERP and POS system.                                                                     |
| ⚙️ **External hw_proxy**         | Bridge between Odoo POS and a physical ESC/POS printer (running at `192.168.1.146:9002`).    |
| 📊 **FastAPI hw_status_service** | Local service offering status UI, OpenAPI/Docs, and **test print** features.                 |
| 🔒 **Traefik v3.4.0**            | Reverse proxy handling HTTPS routing, local certificates, and HTTP/3.                        |
| 🧩 **POS Indv Receipt Add-on**   | Prints one ticket per unit from the POS receipt screen — ideal for bars, events, and kiosks. |
| 🗄️ **PostgreSQL 13.21**         | Database backend for Odoo (persistent volume).                                               |

All components run locally in Docker containers, except for the optional **`hw_proxy`**, which runs on the host for direct access to printer hardware.

---

## 🧭 Repository Structure

```bash
├── docker-compose/           # Main Docker Compose and environment templates
│   ├── traefik/              # Traefik configs, routers, and local certs
│   ├── postgres/pgdata/      # PostgreSQL persistent storage
│   ├── odoo/                 # Odoo data, config, and custom add-ons
│   ├── hw_status.env         # FastAPI hw_status_service environment
│   └── docker-compose.yml    # Main composition file
├── docker_offline/           # Offline deployment mode
├── hw_status/                # FastAPI hardware status dashboard (in-stack)
├── hw_proxy/                 # Local printer bridge (runs externally on host)
├── services/odoo_server/     # Odoo 18 server configuration and build context
├── odoo_addons/              # Extra Odoo add-ons (including POS Indv Receipt)
├── custom_fonts/             # Offline fonts for Odoo reports and POS
├── windows_scripts/          # Helper scripts for Windows/WSL2
├── ODOO_SERVER.md            # Advanced Odoo server configuration notes
├── LICENSE                   # Apache-2.0 license
└── README.md                 # This file
```

---

## 🧩 System Architecture

### Data Flow

1. **Traefik** terminates HTTPS and routes requests:

   * `/` → `fiesta_odoo:8069` (Odoo)
   * `/hw_status` → `hw_status_service:8015`
   * `/hw_proxy` → external host `192.168.1.146:9002`
2. **Odoo POS** communicates securely with `hw_proxy` for direct printing.
3. **hw_status_service** offers a browser dashboard for printer/system monitoring and test printing.
4. **PostgreSQL** stores Odoo data; all services run locally under the `odoo_network`.

---

## 🚀 Quick Start

### 📘 Table of Contents

1. [Requirements](#1️⃣-requirements)
2. [Clone the Repository](#2️⃣-clone-the-repository)
3. [`hw_proxy` Service](#3️⃣-hw_proxy-service)
4. [Install, Secure, and Configure Docker (with mTLS and userns-remap)](#4️⃣-install-secure-and-configure-docker-with-mtls-and-userns-remap)
5. [Set up Docker Compose](#5️⃣-set-up-docker-compose)
6. [Configure Environment](#6️⃣-configure-environment)
7. [Launch the Stack](#7️⃣-launch-the-stack)

---

### 1️⃣ Requirements

Ensure your host meets the prerequisites:

* **Ubuntu 22.04+ (recommended)** or compatible Linux
* **Docker ≥ 24** and **Docker Compose v2**
* **sudo/root access** for service and device configuration
* (Optional) **POS printer** connected via USB or serial
* (Optional) **Make**, **curl**, and **NetworkManager** for utilities

---

### 2️⃣ Clone the Repository

Clone this repository to your preferred directory, ideally `/opt/Odoo_rafa`:

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/mano8/Odoo_rafa.git
sudo chown -R $USER:$USER Odoo_rafa
cd Odoo_rafa
```

---

### 3️⃣ [`hw_proxy` Service](./fiesta_pos/hw_proxy/hw_proxy/README.md)

The **`hw_proxy`** FastAPI service runs **directly on the host machine** and acts as a bridge between **Odoo POS** and **local hardware** such as printers and cash drawers.

It provides API endpoints for:

* 🖨️ **ESC/POS printer control** (e.g., Posiflex PP6800, Epson TM series)
* 💾 **Database backups** (PostgreSQL dump + ZIP download)
* 🔌 **System actions** (reboot, shutdown, restart containers)
* ⚙️ **Serial port configuration** and **hardware enumeration**

Setup includes:

* Creating a dedicated `hw_user`
* Configuring `udev` permissions for `/dev/tty*`
* Enabling `systemd` services (`hw_proxy.service`, `serial-config.service`)

📘 Full setup → [View hw_proxy README](./fiesta_pos/hw_proxy/hw_proxy/README.md)

---

### 4️⃣ [Install, Secure, and Configure Docker (with mTLS and `userns-remap`)](./docker/README.md)

Install and harden Docker Engine for a secure local environment:

* Installs Docker CE from the official repository
* Enables **user namespace remapping** for non-root containers
* Configures **mutual TLS (mTLS)** for Docker API access
* Creates an isolated **dummy interface** (`docker0-mgmt`)
* Optionally configures **journald** for centralized log rotation

📘 Detailed instructions → [View Docker Setup README](./docker/README.md)

---

### 5️⃣ [Set up Docker Compose](./docker-compose/README.md)

Use Docker Compose to orchestrate Odoo, PostgreSQL, Traefik, and `hw_status_service`.

Features include:

* **Online & Offline** deployment support
* **Systemd auto-start** integration (`odoo-pos.service`)
* **journald-based logging** for each container
* Pre-built environment templates and configuration examples

📘 Deployment guide → [View Docker Compose README](./docker-compose/README.md)

---

### 6️⃣ Configure Environment

Copy and customize the environment files:

```bash
cp ./env.example.txt .env
cp ./hw_proxy.env.example.txt ./hw_proxy.env
nano .env
nano ./hw_proxy.env
```

Example configuration:

```env
DB_HOST=fiesta_db
DB_DATABASE=odoo
DB_USER=odoo
DB_PASSWORD=changethis
```

Odoo automatically initializes the database on first run.
The same credentials should appear in `odoo/config/odoo.conf`.

---

### 7️⃣ Launch the Stack

Build and start all containers:

```bash
sudo docker compose -f docker-compose/docker-compose.yml up -d --build
```

Access the main services:

| Service               | URL                                                                                        | Description                   |
| --------------------- | ------------------------------------------------------------------------------------------ | ----------------------------- |
| **Odoo ERP / POS**    | [https://traefik-client.local:9000](https://traefik-client.local:9000)                     | Main Odoo web interface       |
| **Hardware Status**   | [https://traefik-client.local:9001/hw_status](https://traefik-client.local:9001/hw_status) | FastAPI dashboard             |
| **Hardware Proxy**    | [https://traefik-client.local:9001/hw_proxy](https://traefik-client.local:9001/hw_proxy)   | Bridge to local host hardware |
| **Traefik Dashboard** | [http://localhost:8080](http://localhost:8080)                                             | Reverse proxy monitor         |

> 🧩 Import the local CA (`docker-compose/traefik/certs/ca.pem`) into your browser/OS to avoid HTTPS warnings.

---

✅ **Your Odoo POS Stack is ready.**
You now have a locally secure, fully containerized Odoo 18 environment with Traefik, PostgreSQL, hardware proxy integration, and automated service management.

---

## 🖨️ Hardware Integration

### 🔌 External hw_proxy

* Runs outside the compose stack (on host at `192.168.1.146:9002`).
* Accepts HTTPS requests from Odoo POS via Traefik’s `/hw_proxy` router.
* Bridges requests directly to your **ESC/POS printer** (USB, serial, or TCP).

**Example setup (`hw_proxy/config.py`):**

```python
PRINTER_DEVICE = "/dev/ttyUSB0"  # or COM3 on Windows
BAUDRATE = 9600
```

---

### 📊 hw_status_service (FastAPI)

Provides a browser-based dashboard for monitoring and testing printers.

#### hw_status_service Features

* Real-time printer connection status
* CPU, memory, uptime metrics
* “Test Print” button for quick validation
* OpenAPI, Docs, and Redoc at `/hw_status` endpoints

---

## 🧾 Odoo Add-on: POS Individual Receipt

Enhances Odoo 18 POS with per-unit ticket printing.

### Odoo Add-on Features

* Adds **“Print Product Tickets”** button on receipt screen
* Popup to select items from the current order
* Prints **one ticket per quantity unit**
* Tickets use standard POS header/footer

#### Odoo Add-on Installation

1. Already included under `odoo_addons/pos_indv_receipt/`
2. Automatically updated on container start (`-u pos_indv_receipt --dev=css`)
3. To force update manually:

   ```bash
   docker compose restart fiesta_odoo
   ```

---

## 🧰 Maintenance & Utilities

### View Logs

```bash
docker compose logs -f traefik
docker compose logs -f fiesta_odoo
docker compose logs -f hw_status_service
```

### Rebuild the Stack

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Backup

```bash
docker exec -t fiesta_db pg_dump -U odoo odoo > backup.sql
```

---

## 🔐 Security

* HTTPS enforced by Traefik with local CA.
* Default passwords must be changed (`DB_PASSWORD`, Odoo admin).
* Non-root containers where possible.
* Only trusted LAN access recommended.
* `extra_hosts` mapping keeps fonts offline (`fonts.odoo.com → local IP`).

---

## 🧪 Troubleshooting

| Issue                  | Possible Fix                                                                   |
| ---------------------- | ------------------------------------------------------------------------------ |
| **POS not printing**   | Check if `hw_proxy` service at `192.168.1.146:9002` is running and accessible. |
| **Test print fails**   | Confirm correct printer port and permissions.                                  |
| **Odoo HTTPS warning** | Trust local CA in your OS.                                                     |
| **Add-on not visible** | Update apps list and confirm add-on path is mounted.                           |

---

## 📜 License

Licensed under the **Apache License 2.0**.
See [LICENSE](./LICENSE) for details.

---

## 👨‍💻 Developer

**Developed and maintained by [Eli Serra](https://github.com/mano8)**
Using open-source technologies: **Odoo 18**, **FastAPI**, **PostgreSQL**, **Docker**, and **Traefik v3.4.0**
