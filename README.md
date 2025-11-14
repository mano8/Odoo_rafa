# Odoo_rafa

**Production-ready Odoo server setup** with Docker Compose, optional offline mode, hardware proxy helpers, and custom add-ons/fonts.

> This repository contains the infrastructure and assets used to run “Odoo server” in a reproducible way.

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](#license)

---

## ✨ Features

* **Dockerized Odoo stack** — consistent local or server deployment.
* **Online & Offline modes** — run fully offline when needed (see `docker_offline/`).
* **Custom add-ons** — place modules under `odoo_addons/`; includes POS-related assets.
* **Hardware proxy helpers** — scripts/configs under `hw_proxy/` for POS/IoT.
* **Custom fonts** — drop fonts under `custom_fonts/` and enable them in Odoo.
* **Windows helpers** — utilities in `windows_scripts/` for Windows environments.
* **Clear service layout** — `services/odoo_server` holds build and config for Odoo. ([GitHub][1])

---

## 🧭 Repository structure

```
.
├─ docker-compose/        # Compose files and env templates for the main stack
├─ docker_offline/        # Compose + assets for offline deployments
├─ services/
│  └─ odoo_server/        # Odoo service build context, configs, entrypoints
├─ hw_proxy/              # Hardware proxy helpers (POS/IoT)
├─ hw_status/             # Hardware status utilities
├─ odoo_addons/           # Custom/local Odoo add-ons
├─ custom_fonts/          # TTF/OTF fonts to use inside Odoo
├─ windows_scripts/       # Windows helper scripts (optional)
├─ ODOO_SERVER.md         # Extra notes specific to the Odoo server
├─ LICENSE                # Apache-2.0
└─ README.md              # You are here
```

> See the repo root for the actual folders and files. ([GitHub][1])

---

## 🏗️ Prerequisites

* **Docker** 24+ and **Docker Compose v2**
* 4 GB RAM (minimum), SSD recommended
* (Optional) **Make** for convenience targets
* (Optional) On Windows, **WSL2** recommended

---

## 🚀 Quick start

> The commands below assume you’re in the repo root.

1. **Configure environment**

Create a `.env` (or copy from the templates under `docker-compose/`) and set at least:

```env
# Core
ODOO_VERSION=18.0
ODOO_DB_HOST=postgres
ODOO_DB=odoo
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=odoo

# Admin
ODOO_MASTER_PASSWORD=change-this
ODOO_ADMIN_EMAIL=admin@example.com

# Paths (mounted volumes)
ADDONS_PATH=/var/lib/odoo/addons
CUSTOM_ADDONS=/mnt/extra-addons

# Optional proxy
HTTP_PORT=8069
LONGPOLLING_PORT=8072
```

2. **Place your modules & fonts**

* Put custom modules in `odoo_addons/`.
* Put fonts in `custom_fonts/` (TTF/OTF).

3. **Start the stack**

```bash
# Online mode (default)
docker compose -f docker-compose/docker-compose.yml up -d --build

# First-time logs:
docker compose -f docker-compose/docker-compose.yml logs -f odoo
```

Then open: `http://localhost:8069`

4. **Create the first database**

Use the web UI and the `ODOO_MASTER_PASSWORD` you set in `.env`.

---

## 📴 Offline mode

When you need to run without internet connectivity:

```bash
docker compose -f docker_offline/docker-compose.offline.yml up -d --build
```

* Make sure any required images are pre-pulled on the host.
* Confirm volumes for add-ons and fonts are mounted as in online mode.

---

## 🧩 Add-ons & POS assets

* Drop any custom modules under `odoo_addons/` and ensure the path is listed in the container’s `--addons-path` (the provided Compose files typically mount this folder inside the container).
* If you’re using the POS, place POS-related modules (e.g., receipt customizations) here as well. A ZIP named like `pos_indv_receipt_v18-...zip` is included in the repo root for convenience—extract it into `odoo_addons/` to use. ([GitHub][1])

---

## 🖨️ Hardware proxy (IoT / POS)

The `hw_proxy/` folder contains helper scripts/configs for running a hardware proxy (useful for POS peripherals such as printers, barcode scanners, etc.). Integrate by:

1. Connecting the container or host to the device (Serial/USB/TCP).
2. Starting the hw proxy service/container as documented in `hw_proxy/` (or integrate with your main Compose file).
3. Configuring Odoo → **Point of Sale** → **IoT**/**Hardware Proxy** to point to the proxy endpoint.

> See also `hw_status/` for basic status checks. ([GitHub][1])

---

## 🅰️ Custom fonts

1. Put `.ttf` or `.otf` files into `custom_fonts/`.
2. Ensure the Compose file mounts this folder into the Odoo container (commonly under `/usr/share/fonts/custom`).
3. Rebuild/restart Odoo so fonts are picked up.
4. Select fonts in reports/website as needed.

A `fonts.zip` is included at the repo root for convenience. Extract it into `custom_fonts/`. ([GitHub][1])

---

## ⚙️ Configuration & service files

* The core Odoo service configuration lives under `services/odoo_server/` (Dockerfile, entrypoints, and any config files). Adjust build args and paths there if you need to change Odoo version or base image. ([GitHub][2])
* Additional guidance and notes: see **`ODOO_SERVER.md`**. ([GitHub][1])

---

## 🧪 Health checks & logs

```bash
# Follow Odoo logs
docker compose -f docker-compose/docker-compose.yml logs -f odoo

# If using a Postgres service in the same stack:
docker compose -f docker-compose/docker-compose.yml logs -f postgres
```

If Odoo doesn’t become ready, confirm:

* Database credentials & connectivity
* Add-on path mounts and permissions
* That any POS/hardware services the instance expects are reachable

---

## 💾 Backup & restore

**Backup**

* From the Odoo UI: *Database Manager* → *Backup* (includes filestore if selected).
* Or from the host (if filestore mapped): archive the database dump + `odoo/filestore/<dbname>`.

**Restore**

* From the Odoo UI: *Database Manager* → *Restore* (supply dump).
* Re-create the `filestore` directory content if you backed it up separately.

---

## 🔄 Updating

1. Pull changes to this repository.
2. Review diffs in `docker-compose/` and `services/odoo_server/`.
3. Rebuild and restart:

```bash
docker compose -f docker-compose/docker-compose.yml pull
docker compose -f docker-compose/docker-compose.yml up -d --build
```

4. Upgrade installed modules in Odoo (Apps → *Upgrade*).

---

## 🧰 Windows helpers

The `windows_scripts/` folder contains helper scripts for Windows hosts. Use them to streamline local development on Windows (consider WSL2 for better performance). ([GitHub][1])

---

## 🔐 Security checklist

* Change default passwords in `.env`.
* Restrict external access (use a reverse proxy and TLS in production).
* Keep Docker images updated.
* Limit add-on sources to trusted code.
* Back up the database and filestore regularly.

---

## ❓ Troubleshooting

* **“Database creation failed”** → Check `ODOO_MASTER_PASSWORD`, DB host, user, password, and that Postgres is reachable.
* **“Module not found”** → Verify the add-on path is mounted and included in `--addons-path`; module folder name must match the manifest.
* **POS devices not detected** → Verify `hw_proxy` service is running and reachable from the Odoo container/network.
* **Fonts not applied** → Rebuild/restart the container after adding fonts and clear the Odoo cache.

---

## 📄 License

This project is licensed under the **Apache-2.0** license. See [LICENSE](./LICENSE) for details. ([GitHub][1])

---

## 🙌 Acknowledgements

Thanks to the Odoo community and contributors of third-party modules used with this setup.

---

### Notes

* If you maintain separate Compose files per environment (dev/stage/prod), keep them under `docker-compose/` and document any differences (ports, volumes, env).
* For detailed server notes or non-Docker installs, see **`ODOO_SERVER.md`**. ([GitHub][3])
