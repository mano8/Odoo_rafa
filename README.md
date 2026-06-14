# 🧾 Odoo Rafa's Local POS Stack

**Self-contained local Odoo 18 ecosystem** integrating a FastAPI hardware proxy, a browser-based status dashboard, Prometheus/Grafana observability, and Traefik with locally trusted SSL — extended by custom POS add-ons for structured receipt printing.

> Eliminates the need for Odoo IoT Box while providing full HTTPS, ESC/POS JSON printing, disaster-recovery backups, and live hardware monitoring.

[License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)

---

## 📋 What's in this stack

| Component | Description |
| --- | --- |
| 🧱 **Odoo 18.0** | Main ERP and POS system |
| ⚙️ **hw_proxy** (host service) | FastAPI bridge between Odoo POS and ESC/POS printer/cash drawer; exposes Prometheus metrics |
| 📊 **hw_status** (in-stack) | Browser dashboard: printer status, service logs, system metrics, test-print button |
| 📈 **Prometheus + Grafana** | Scrapes hw_proxy metrics; pre-provisioned dashboard for print jobs, latency, disk, printer status |
| 🔒 **Traefik v3.4.0** | Reverse proxy with local CA TLS; mkcert-based cert renewal |
| 🧩 **pos_json_printer** | POS add-on: JSON → ESC/POS pipeline replacing raster PNG; session report, hamburger print |
| 🧩 **pos_indv_receipt** | POS add-on: one ticket per unit from the receipt screen |
| 🗄️ **PostgreSQL 13** | Database backend (persistent bind mount) |

All components run in Docker except **hw_proxy**, which runs on the host for direct serial/USB hardware access.

---

## 🧭 Repository Structure

```text
├── docker-compose/
│   ├── odoo_prod/            # Main compose stack (Odoo, Postgres, Traefik, hw_status)
│   │   ├── docker-compose.yml
│   │   ├── traefik/          # Traefik config, dynamic routes, TLS certs
│   │   ├── postgres/pgdata/  # PostgreSQL persistent storage (bind mount)
│   │   └── odoo/             # Odoo data, config, add-ons
│   ├── monitoring/           # Prometheus + Grafana stack
│   └── scripts/              # Shared shell scripts (backup, restore, cert renewal, etc.)
├── docker_offline/           # Air-gapped deployment (vendored wheels + image tarballs)
├── docker/                   # Docker daemon setup (userns-remap, mTLS, dummy interface)
├── hw_proxy/                 # Host printer bridge (FastAPI, ESC/POS, Prometheus metrics)
├── hw_status/                # In-stack status dashboard (FastAPI)
├── odoo_addons/              # pos_json_printer, pos_indv_receipt
├── monitoring/               # Grafana dashboards and provisioning
├── services/odoo_server/     # systemd unit files
├── ODOO_SERVER.md            # Server configuration and operations notes
├── SECURITY.md               # Security hardening checklist
└── README.md                 # This file
```

---

## 🧩 System Architecture

### Data Flow

1. **Traefik** terminates HTTPS on port `9001` and routes:
   - `/` → `fiesta_odoo:8069` (Odoo, port `9000`)
   - `/hw_status` → `hw_status_service:8015`
   - `/hw_proxy` → host service `10.254.254.1:9002` (management interface)
2. **Odoo POS** prints via `hw_proxy` through Traefik TLS at port `9001`.
3. **hw_status** provides a browser dashboard for real-time diagnostics and test printing.
4. **Prometheus** scrapes `hw_proxy` metrics every 15 s; **Grafana** visualises them.

---

## 🚀 Quick Start

### 📘 Table of Contents

1. [Requirements](#1️⃣-requirements)
2. [Clone the Repository](#2️⃣-clone-the-repository)
3. [`hw_proxy` Service](#3️⃣-hw_proxy-service)
4. [Post-Deploy Security Hardening](#4️⃣-post-deploy-security-hardening)
5. [Install, Secure, and Configure Docker](#5️⃣-install-secure-and-configure-docker-with-mtls-and-userns-remap)
6. [Set up Docker Compose](#6️⃣-set-up-docker-compose)
7. [Configure Environment](#7️⃣-configure-environment)
8. [Launch the Stack](#8️⃣-launch-the-stack)

---

### 1️⃣ Requirements

- **Ubuntu 22.04+** or compatible Linux
- **Docker ≥ 24** and **Docker Compose v2**
- **Make** (`sudo apt install make`)
- **mkcert** (`sudo apt install mkcert`) — for TLS cert management
- **sudo/root access** for service and device configuration
- (Optional) **POS printer** connected via USB or serial
- (Optional) **curl**, **rsync**, **NetworkManager**

---

### 2️⃣ Clone the Repository

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/mano8/Odoo_rafa.git
sudo chown -R $USER:$USER Odoo_rafa
cd Odoo_rafa
```

#### Automated deployment with `make`

```bash
make help           # list all available targets
```

First-time setup on a fresh machine:

```bash
make install        # create hw_user, certs, deploy hw_proxy, enable services, build images
# edit .env files as instructed by the output, then:
make up             # generate odoo.conf, fix volumes, start all containers
```

Day-to-day operations:

```bash
make stack-up               # rebuild images and start full stack (online)
make stack-up OFFLINE=1     # same, air-gapped — vendors wheels and loads image tarballs
make update-hw-proxy        # pull + redeploy hw_proxy venv + restart service
make update-odoo-addon      # run addon update script + restart Odoo container
make update                 # full update: hw_proxy + Docker rebuild + restart
make status                 # show all systemd services and Docker container status
make backup                 # PostgreSQL logical dump (pg_dump)
make backup-volumes         # snapshot pgdata + filestore → /opt/backups/odoo_rafa/ (max 5)
make restore-volumes BACKUP=<path>       # restore from a snapshot directory
make monitoring-reload                   # reload Prometheus config + restart Grafana
make monitoring-reload-prometheus        # SIGHUP Prometheus — zero downtime
make monitoring-reload-grafana           # restart Grafana to pick up dashboard changes
make certs-status                        # show expiry dates for all TLS/mTLS certs
make certs-renew                         # auto-renew certs expiring within 30 days
make certs-force-renew                   # force-regenerate all leaf certs
make certs-rotate-ca                     # MANUAL: rotate CA (interactive, destructive)
make logs                                # follow odoo_prod container logs
```

---

### 3️⃣ [`hw_proxy` Service](./hw_proxy/README.md)

Runs directly on the host machine; bridges Odoo POS to local hardware.

- ESC/POS printer control (Posiflex PP6800, Epson TM series, others)
- Cash drawer trigger
- Database backup via `pg_dump` through the container
- System actions: reboot, shutdown
- Prometheus metrics endpoint at `/hw_proxy/metrics`

📘 Full setup → [View hw_proxy README](./hw_proxy/README.md)

---

### 4️⃣ [Post-Deploy Security Hardening](./SECURITY.md)

- Add `hw_user` to `dialout` and `lp` groups
- Configure `ufw` firewall rules
- Change all default passwords
- Review production environment flags

📘 Full checklist → [View SECURITY.md](./SECURITY.md)

---

### 5️⃣ [Install, Secure, and Configure Docker (with mTLS and `userns-remap`)](./docker/README.md)

- Docker CE from the official repository
- User namespace remapping (non-root containers)
- Mutual TLS for Docker API access
- Isolated dummy management interface (`10.254.254.1`)
- journald log rotation

📘 Detailed instructions → [View Docker Setup README](./docker/README.md)

---

### 6️⃣ [Set up Docker Compose](./docker-compose/README.md)

- Online and offline deployment
- systemd auto-start (`odoo-pos.service`)
- journald-based container logging
- Pre-built environment templates

📘 Deployment guide → [View Docker Compose README](./docker-compose/README.md)

---

### 7️⃣ Configure Environment

```bash
cp docker-compose/odoo_prod/env.example.txt docker-compose/odoo_prod/.env
nano docker-compose/odoo_prod/.env
```

Key variables:

```env
DB_HOST=fiesta_db
DB_DATABASE=odoo
DB_USER=odoo
DB_PASSWORD=changethis
```

Odoo generates `odoo.conf` from `.env` on first `make up`.

---

### 8️⃣ Launch the Stack

```bash
make up
```

Access the main services:

| Service | URL | Description |
| --- | --- | --- |
| **Odoo ERP / POS** | `https://traefik-client.local:9000` | Main Odoo interface |
| **Hardware Status** | `https://traefik-client.local:9001/hw_status` | FastAPI dashboard |
| **Hardware Proxy** | `https://traefik-client.local:9001/hw_proxy` | Printer bridge |
| **Grafana** | `http://localhost:3000` | hw_proxy metrics dashboard |
| **Traefik Dashboard** | `http://localhost:8080` | Reverse proxy monitor |

> Import `docker-compose/odoo_prod/traefik/certs/ca.pem` into your browser/OS trust store to avoid HTTPS warnings.

---

## 🖨️ Hardware Integration

### hw_proxy

- Runs on the host (uvicorn at `10.254.254.1:9002`).
- Traefik TLS-terminates on port `9001` and forwards — **Odoo POS must use port `9001`**, not `9002`.
- Exposes a Prometheus metrics endpoint scraped by the monitoring stack.

---

### hw_status Dashboard

Browser-based dashboard (in-stack, no host dependencies):

- Real-time printer connection and paper status
- Dynamic services status grid (systemd + Docker)
- Service log viewer (journald via shell scripts)
- CPU, memory, uptime
- "Imprimir Ticket de Prueba" — sends a full test receipt through the ESC/POS JSON pipeline

---

### Prometheus + Grafana

The monitoring stack (`docker-compose/monitoring/`) is started alongside `odoo_prod` by `make up`.

Grafana is provisioned from `monitoring/grafana/` (dashboards and datasources in git).
After editing `prometheus.yml` or Grafana provisioning files:

```bash
make monitoring-reload-prometheus   # zero-downtime Prometheus config reload
make monitoring-reload-grafana      # restart Grafana to pick up dashboard changes
```

---

## 🧾 Odoo Add-on: POS JSON Printer (`pos_json_printer`)

Replaces the raster PNG receipt path with a structured **JSON → ESC/POS** pipeline.

- Regular receipts render the OWL `OrderReceipt` component, walk the resulting DOM,
  and convert it to typed lines sent to `hw_proxy`
- Session/Z-report builds lines directly from `get_sale_details` RPC data — DOM
  scanning was unreliable here due to `xml:space="preserve"` newlines in text nodes
- Session report and hamburger "Print Report" both route through the same pipeline
- ~5 ms encode time vs ~25 ms for raster PNG
- Euro (€) and Latin characters via CP858 encoding
- Section headers translated via `_t()` (Spanish included)
- Falls back to standard Odoo raster print on error

Deploy after changes:

```bash
make update-odoo-addon   # syncs files + restarts Odoo; version bump triggers auto-upgrade
```

---

## 🧾 Odoo Add-on: POS Individual Receipt (`pos_indv_receipt`)

Adds a **"Print Product Tickets"** button on the receipt screen. Popup lets the cashier select items; prints one ticket per quantity unit. Ideal for bars, events, and kiosks.

Price information on the individual tickets is controlled from **Point of Sale → Settings → Individual Tickets**:

- **Unit Price (excl. VAT)** — prints the VAT-excluded unit price in the right column.
- **Unit Price (VAT incl.)** — also prints a VAT line and the VAT-included total.

Both default to off, so tickets carry no price unless one option is enabled.

---

## 🔐 Certificate Management

Certificates are managed with `mkcert`. The CA lives at `/opt/Odoo_rafa/mkcert-ca` on the server (outside the repo).

```bash
make certs-status           # inspect all cert expiry dates (no changes)
make certs-renew            # renew any cert expiring within 30 days (idempotent)
make certs-force-renew      # force-regenerate all leaf certs
make certs-rotate-ca        # MANUAL — interactive CA rotation (requires typing ROTATE)
```

Traefik certs (CA + server) are valid for 2 years; Docker mTLS certs for 10 years.
After any leaf renewal only Traefik restarts. CA rotation also restarts the Docker daemon.

---

## 🧰 Maintenance

### Disaster Recovery

```bash
# Create snapshot (~120 MB compressed, max 5 kept):
make backup-volumes
# → /opt/backups/odoo_rafa/<datetime>/pgdata.tar.gz + odoo_data.tar.gz

# Restore from a snapshot:
make restore-volumes BACKUP=/opt/backups/odoo_rafa/2026-05-30_14-00-00
# Stops all stacks, extracts with original uid/gid, re-applies ownership, restarts.
```

### View Logs

```bash
make logs                    # odoo_prod containers
make monitoring-logs         # Prometheus + Grafana
docker compose -f docker-compose/odoo_prod/docker-compose.yml logs -f traefik
```

### Rebuild the Stack

```bash
make down && make stack-up
```

---

## 🧪 Troubleshooting

| Issue | Possible Fix |
| --- | --- |
| **POS not printing** | `systemctl status hw_proxy`; Traefik must forward `9001 → 9002` |
| **Test print fails** | Check correct serial port and hw_user permissions (`dialout`, `lp`) |
| **Odoo HTTPS warning** | Import `traefik/certs/ca.pem` into your OS/browser trust store |
| **Grafana "No data"** | Confirm `hw_proxy` is running and Prometheus scrape target is reachable |
| **Add-on not visible** | Update apps list; confirm add-on path is mounted in `docker-compose.yml` |

---

## 🔐 Security

- HTTPS enforced end-to-end via Traefik + local CA.
- Default passwords must be changed (`DB_PASSWORD`, Odoo admin, Grafana admin).
- User namespace remapping — containers run as non-root on the host.
- hw_proxy bound only to the management interface (`10.254.254.1`), not the LAN.
- Only trusted LAN subnets (`192.168.x.x`, `10.x.x.x`, `172.16–31.x.x`) accepted by hw_proxy IP filter.

---

## 📜 License

Licensed under the **Apache License 2.0**.
See [LICENSE](./LICENSE) for details.

---

## 👨‍💻 Developer

**Developed and maintained by [Eli Serra](https://github.com/mano8)**
Using open-source technologies: **Odoo 18**, **FastAPI**, **PostgreSQL**, **Docker**, **Traefik v3.4.0**, **Prometheus**, **Grafana**
