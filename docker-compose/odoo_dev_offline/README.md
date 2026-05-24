# Dev Offline Stack — Setup & Debug Guide

Full-stack development environment for Odoo + hw_proxy + hw_status, running entirely
offline (no internet required after the initial wheel build). No Traefik — direct port
mapping keeps the dev loop simple.

## Stack overview

| Service | Port | Notes |
| --- | --- | --- |
| Odoo 18 | 9000 | Auto-initialises DB on first run |
| hw_proxy | 9002 | FastAPI — ESC/POS printer proxy |
| hw_status | 8015 | FastAPI — hardware status dashboard |
| Postgres 13 | (internal) | Bridge network only |

---

## Prerequisites

### Windows 11

- **WSL2** installed and set as default (`wsl --install` if not present — see Step 3)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend enabled
- [usbipd-win](https://github.com/dorssel/usbipd-win) installed via `winget` (full instructions in Step 3)
- WSL2 kernel >= 5.10.16 — ships with Windows 11, no manual update needed

### Linux

- Docker Engine + Docker Compose plugin
  `sudo apt install docker.io docker-compose-plugin`
- User in the `docker` and `dialout` groups
  `sudo usermod -aG docker,dialout $USER` (re-login after)

### macOS

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Intel or Apple Silicon)
- Xcode Command Line Tools (for `make`): `xcode-select --install`
- **Note:** Docker Desktop for macOS cannot pass USB devices to containers.
  Hardware printer testing requires running hw_proxy natively — see Step 3.

---

## Step 1 — Build offline wheels

This step requires internet access and only needs to run **once** (or when requirements
change). Wheels are written to `hw_proxy/wheelhouse_dev/` and `hw_status/wheelhouse_dev/`
(both gitignored). Copy them to any air-gapped machine alongside the repo.

> The dev images (`Dockerfile.offline.dev`) are based on `python:3.11-slim` and install
> system packages via `apt` at build time — no separate base-image build required.
> Only the Python wheels need to be pre-downloaded.

### Windows 11 — Docker-based (no `make` required)

```powershell
cd docker-compose/odoo_dev_offline
docker compose -f docker-compose.init.yml run --rm wheel-builder
```

This spins up a `python:3.11-slim` container, downloads all wheels, and exits.

### Linux and macOS — Docker-based (recommended)

```bash
cd docker-compose/odoo_dev_offline
docker compose -f docker-compose.init.yml run --rm wheel-builder
```

### Linux and macOS — make-based alternative

```bash
cd docker_offline
make -f Makefile.wheels dev-all
```

---

## Step 2 — Configure environment files

```bash
# Linux / macOS
cd docker-compose/odoo_dev_offline/
cp .env.example          .env
cp hw_proxy.env.example  hw_proxy.env
cp hw_status.env.example hw_status.env
```

```powershell
# Windows 11 (PowerShell)
cd docker-compose/odoo_dev_offline
Copy-Item .env.example          .env
Copy-Item hw_proxy.env.example  hw_proxy.env
Copy-Item hw_status.env.example hw_status.env
```

**Minimum values to change in `.env`:**

```dotenv
DB_PASSWORD="a-strong-password"
HOST_IP="<your LAN IP>"      # used for the fonts.odoo.com offline workaround
```

**Minimum value to change in `hw_proxy.env` and `hw_status.env`:**

```dotenv
SECRET_KEY="<random 32+ char string>"   # alphanumeric + symbols
```

> `DB_PASSWORD` lives only in `.env` — hw_proxy and hw_status are FastAPI services that do not connect to Postgres directly.
>
> The config validator rejects the literal value `changethis` — any other non-trivial string works for local dev.

---

## Step 3 — Forward the USB printer

The Posiflex PP6800 uses USB-CDC/ACM serial (`/dev/ttyACM0`, vendor `0x0d3a`).

### Windows 11 — usbipd-win

Docker Desktop cannot access USB devices directly. `usbipd-win` is a Windows service
that forwards USB devices into WSL2 so Docker can see them.

#### 0. Verify WSL2 is installed (prerequisite)

`usbipd attach --wsl` requires **WSL2** (not WSL1). Open **Windows PowerShell** (not a
WSL terminal) and check:

```powershell
wsl --status
```

You need `Default Version: 2`. If WSL is not installed yet:

```powershell
wsl --install          # installs WSL2 + Ubuntu, requires reboot
```

If WSL is installed but defaults to version 1:

```powershell
wsl --set-default-version 2
```

#### 1. Install usbipd-win (one-time)

Open **PowerShell as Administrator** (right-click the Start menu → "Windows PowerShell
(Admin)" or "Terminal (Admin)") and run:

```powershell
winget install --id dorssel.usbipd-win
```

`winget` ships pre-installed on Windows 11 — no extra setup needed. The installer adds
a Windows service and puts `usbipd` on your PATH.

Close and reopen PowerShell after install (PATH is refreshed on new sessions). Confirm:

```powershell
usbipd --version
```

#### 2. Bind the printer (one-time per machine, requires admin)

Plug in the Posiflex PP6800. In any PowerShell, list all USB devices:

```powershell
usbipd list
```

Example output:

```text
BUSID  VID:PID    DEVICE                        STATE
1-8    0d3a:0368  USB Serial Device (COMx)      Not shared   ← printer (Posiflex PP6800)
2-3    04f3:0103  HID Keyboard                  Not shared
2-4    046d:c08b  USB Mouse                     Not shared
```

Find the row where `VID:PID` is **`0d3a:0368`**. The device name will vary by OS
language (e.g. "USB Serial Device", "Périphérique série USB") — use the VID:PID to
identify it reliably. Note its `BUSID` (in this example `1-8`).

> **Warning:** do NOT bind a keyboard, mouse, or USB receiver. Binding is safe on its
> own (the device stays usable in Windows), but attaching it to WSL2 will disconnect it
> from Windows input until detached.
>
> If you accidentally bound the wrong device, unbind it (admin required):
>
> ```powershell
> usbipd unbind --busid 2-3    # replace with the wrong BUSID
> ```
>

Open **PowerShell as Administrator** (right-click Start → "Terminal (Admin)"), then bind
only the printer:

```powershell
usbipd bind --busid 1-8     # use the BUSID of the 0d3a:0368 row
```

You only need to do this once — the binding survives reboots. After binding, the `State`
column in `usbipd list` changes from `Not shared` to `Shared`.

#### 3. Attach before each session

Docker Desktop runs its Engine inside a special WSL2 distro called **`docker-desktop`**.
USB devices must be attached to that specific distro — not to your default WSL2 distro
(e.g. Ubuntu) — otherwise Docker containers cannot see them.

Every time you start a new dev session, run this in a regular PowerShell **before**
`docker compose up`:

```powershell
usbipd attach --wsl docker-desktop --busid 2-3
```

Verify the device is visible from Docker's perspective:

```powershell
wsl -d docker-desktop ls /dev/ttyACM0
```

Expected output: `/dev/ttyACM0`. If you get "No such file or directory" the attach did
not target the right distro — re-run the attach command above.

When done for the day:

```powershell
usbipd detach --busid 2-3
```

### Linux — direct access

The device is directly accessible. Verify it is recognised after plugging in:

```bash
ls /dev/ttyACM0
# If missing, check dmesg:
dmesg | tail -20
```

Ensure your user is in the `dialout` group (re-login required after adding):

```bash
groups | grep dialout
```

### macOS — printer workaround

Docker Desktop for macOS does not support USB device passthrough.

#### Option A — run hw_proxy natively (recommended for hardware testing)

```bash
cd hw_proxy
python3 -m venv .venv && source .venv/bin/activate
pip install -r hw_proxy/requirements.txt
cp hw_proxy/env.example.txt hw_proxy/.env
# edit .env: set STATIC_BASE_PATH/TEMPLATES_BASE_PATH to absolute local paths
uvicorn hw_proxy.main:app --host 0.0.0.0 --port 9002 --reload
```

The macOS serial device appears as `/dev/tty.usbmodemXXXX` or `/dev/cu.usbmodemXXXX`.
Update `hw_proxy/hw_proxy/core/supported_devices.py` — `devfile` field — accordingly.

#### Option B — develop without hardware

Run the full Docker stack normally. hw_proxy starts but printer calls return a 503.
Useful for working on Odoo or hw_status without a physical printer.

---

## Step 4 — Start the stack

```bash
cd docker-compose/odoo_dev_offline/
docker compose up --build
```

First run: Odoo initialises the database (`base` + `pos_indv_receipt` + `pos_json_printer`) — allow ~2 minutes.
Subsequent runs start in seconds.

---

## Service endpoints

| Service | URL | OpenAPI docs |
| --- | --- | --- |
| Odoo | <http://localhost:9000> | — |
| hw_proxy | <http://localhost:9002/hw_proxy/> | <http://localhost:9002/hw_proxy/docs> |
| hw_status | <http://localhost:8015/hw_status/> | <http://localhost:8015/hw_status/docs> |

---

## Enabling JSON printer in Odoo POS

The `pos_json_printer` addon intercepts receipt printing and sends a compact JSON payload
(~3 KB) to hw_proxy instead of a raster PNG (~56 KB), cutting serial write time from
~4.8 s to ~0.2 s.

### 1. Install the addon

Included automatically on first DB initialisation. To install manually:

1. Open <http://localhost:9000/web?debug=1>
2. Apps → remove the **"Apps"** filter chip → search **`pos_json_printer`** → Install

### 2. Configure the POS

1. POS → Configuration → Settings
2. Under **Hardware** → **Printer** → enable **Print via IoT/Proxy** → toggle on **JSON Printer**
3. Leave **hw_proxy URL** blank for auto-detect (`same hostname:9002`), or enter
   `http://localhost:9002` explicitly if needed
4. Save and restart the POS session

Printing still falls back to the standard PNG path if hw_proxy is unreachable.

---

## Hot-reload

Both service source directories are volume-mounted into their containers:

```text
hw_proxy/hw_proxy/   →  /opt/hw_proxy   (inside container)
hw_status/hw_status/ →  /opt/hw_status  (inside container)
```

Uvicorn runs with `--reload` — saving any `.py` file triggers an automatic restart.
No `docker compose build` required during normal development.

---

## Remote debugging with VS Code

### 1. Enable debugpy

Set `VSCODE_DEBUG=true` in the relevant service env file, then restart that service:

```bash
docker compose restart hw_proxy_service    # debugpy listens on port 5679
docker compose restart hw_status_service   # debugpy listens on port 5678
```

The container **blocks** on startup until VS Code attaches.

### 2. Add attach configurations

Add to your workspace `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach hw_proxy (Docker)",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5679 },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/hw_proxy/hw_proxy",
          "remoteRoot": "/opt/hw_proxy"
        }
      ]
    },
    {
      "name": "Attach hw_status (Docker)",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5678 },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/hw_status/hw_status",
          "remoteRoot": "/opt/hw_status"
        }
      ]
    }
  ]
}
```

Press **F5** (or pick the config in Run & Debug) to attach. Breakpoints in local files
hit inside the container.

---

## Updating Odoo addons

The compose stack mounts `./odoo/addons` (a local copy) rather than the repo source
directly. This avoids unreliable file-change notifications through Windows bind mounts
and ensures Odoo's module upgrade always reads a Docker-native path.

After editing anything under `odoo_addons/`, sync and restart:

```bash
cd docker-compose/odoo_dev_offline
bash update_addon.sh
docker compose restart fiesta_odoo
```

`update_addon.sh` copies `pos_indv_receipt` and `pos_json_printer` from `../../odoo_addons`
into `./odoo/addons`. The Odoo container picks up the changes on next start because
`-u pos_indv_receipt,pos_json_printer` is always passed at startup.

---

## Useful commands

```bash
# Follow logs
docker compose logs -f hw_proxy_service
docker compose logs -f hw_status_service
docker compose logs -f fiesta_odoo

# Restart a single service (e.g. after changing an env file)
docker compose restart hw_proxy_service

# Rebuild a single image (e.g. after adding a dependency)
docker compose build hw_proxy_service

# Stop stack, keep DB volumes
docker compose down

# Full reset — wipes Postgres data and Odoo filestore
docker compose down -v
```

---

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| Service exits immediately on start | Bad env var — `docker compose logs <service>` shows the validation error |
| `device not found: /dev/ttyACM0` | **Win11:** run `usbipd attach --wsl --busid <BUSID>` / **Linux:** check `dmesg`, ensure user is in `dialout` |
| `403 Client IP not allowed` | Host IP not in `TRUSTED_NETWORKS` in `hw_proxy/main.py` — add your IP or the Docker bridge range |
| `ModuleNotFoundError: hw_proxy` | Wheels missing or image not rebuilt — re-run the init step then `docker compose build` |
| `Secret key changethis` error | Set a real value for `SECRET_KEY` in the env file |
| Port already in use | **Win11:** `netstat -ano \| findstr :9002` / **Linux/macOS:** `lsof -i :9002` |
| Odoo takes >5 min on first run | Normal on slow disks — check with `docker compose logs -f fiesta_odoo` |
| `pos_json_printer` not visible in Apps | Enable dev mode (`?debug=1`), remove the **"Apps"** filter chip, then search `pos_` |
| Addon changes not picked up after `restart` | `restart` keeps old container config — use `docker compose up -d --force-recreate fiesta_odoo` |
| macOS: printer calls return 503 | USB passthrough not supported — run hw_proxy natively (see Step 3) |
| Apple Silicon: wheel build fails | The init container auto-selects the host platform; if wheels are missing try adding `--platform linux/amd64` to the `command` in `docker-compose.init.yml` |
