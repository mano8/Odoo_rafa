# Offline Mode

Enables running the entire **Fiesta POS** stack with **no Internet** (air-gapped environment).
The repo already ships offline-capable Dockerfiles and Compose configs — you only need to vendor
the binary artifacts (Docker image tarballs + Python wheel caches) before going offline.

**What to vendor:**

1. **Docker image tarballs** — saved in `docker_offline/*.tar` (gitignored)
2. **Python wheels** — cached in `hw_status/wheelhouse/`, `hw_status/wheelhouse_dev/`, and `hw_proxy/wheelhouse_dev/` (gitignored)

---

## Repository layout

```text
/opt/Odoo_rafa/
├── docker_offline/                 ← run Makefiles from here
│   ├── Makefile                    ← main entry-point: vendors everything in one command
│   ├── Makefile.prepare            ← pull upstream images, build fat base, save to *.tar
│   ├── Makefile.update             ← full prepare + load into local Docker daemon
│   ├── Makefile.wheels             ← download Python wheels for all services
│   ├── python-3.11-slim.tar        ← base image for offline.dev Dockerfiles
│   ├── traefik_v3.4.0.tar
│   ├── postgres_13.21-alpine3.20.tar
│   ├── odoo_18.0.tar
│   ├── python-3.11-fat.tar         ← custom fat base for hw_status prod
│   ├── prometheus_v3.4.0.tar
│   └── grafana_12.0.1.tar
├── hw_proxy/
│   ├── wheelhouse_dev/             ← dev wheels (gitignored)
│   └── hw_proxy/
│       ├── requirements-docker-dev.txt
│       └── Dockerfile.offline.dev
└── hw_status/
    ├── wheelhouse/                 ← prod wheels (gitignored)
    ├── wheelhouse_dev/             ← dev wheels (gitignored)
    └── hw_status/
        ├── requirements-docker.txt
        ├── requirements-docker-dev.txt
        ├── Dockerfile.fat          ← builds the my-python-3.11-fat base image
        ├── Dockerfile.offline.dev  ← dev build using local wheelhouse
        └── Dockerfile.offline      ← prod build using local wheelhouse
```

---

## Workflow A — Prepare on an online machine, deploy offline

### Step 1 · Vendor everything (online machine)

```bash
cd /opt/Odoo_rafa/docker_offline
make
```

Downloads all Python wheels and pulls/builds/saves all Docker images to `*.tar` in one shot.

### Step 2 · Transfer to the offline host

Copy the full repo (or at minimum `docker_offline/*.tar` and the three `wheelhouse*` dirs)
to the target machine.

### Step 3 · Load images and start the stack (offline host)

```bash
cd /opt/Odoo_rafa/docker_offline
make load
```

`make load` vendors everything (no-op if already done) then loads all `*.tar` into the
local Docker daemon. Start the stack afterwards:

```bash
cd /opt/Odoo_rafa/docker-compose/odoo_dev_offline
docker compose up -d
```

---

## Workflow B — Online machine only (no air-gap)

Vendor and load in one shot:

```bash
cd /opt/Odoo_rafa/docker_offline
make load
```

Then start the stack normally.

---

## Makefile targets reference

| Target | What it does |
| ------ | ------------ |
| `make` | Vendor wheels + save images (no load) |
| `make load` | Vendor wheels + save images + load into Docker |
| `make wheels` | Download Python wheels only |
| `make images` | Pull/build/save Docker images only |
| `make clean` | Remove all `*.tar` files and wheelhouse dirs |

---

## Manual fallback commands

Use these if `make` is unavailable on the host.

### Docker images

```bash
cd /opt/Odoo_rafa/docker_offline

# Pull upstream images
docker pull python:3.11-slim
docker pull traefik:v3.4.0
docker pull postgres:13.21-alpine3.20
docker pull odoo:18.0
docker pull prom/prometheus:v3.4.0
docker pull grafana/grafana:12.0.1

# Build custom fat base
docker build \
  -f ../hw_status/hw_status/Dockerfile.fat \
  -t my-python-3.11-fat:latest \
  ../hw_status/hw_status

# Save to tarballs
docker save python:3.11-slim            -o python-3.11-slim.tar
docker save traefik:v3.4.0              -o traefik_v3.4.0.tar
docker save postgres:13.21-alpine3.20   -o postgres_13.21-alpine3.20.tar
docker save odoo:18.0                   -o odoo_18.0.tar
docker save my-python-3.11-fat:latest   -o python-3.11-fat.tar
docker save prom/prometheus:v3.4.0      -o prometheus_v3.4.0.tar
docker save grafana/grafana:12.0.1      -o grafana_12.0.1.tar

# Load on offline host
docker load -i python-3.11-slim.tar
docker load -i traefik_v3.4.0.tar
docker load -i postgres_13.21-alpine3.20.tar
docker load -i odoo_18.0.tar
docker load -i python-3.11-fat.tar
docker load -i prometheus_v3.4.0.tar
docker load -i grafana_12.0.1.tar
```

### Python wheels

Run from repo root. The `--only-binary=:all: --python-version 3.11` flags are required —
without them pip may download source packages that cannot be compiled offline.

```bash
# hw_status — production
pip download --only-binary=:all: --python-version 3.11 \
  --dest hw_status/wheelhouse \
  -r hw_status/hw_status/requirements-docker.txt

# hw_status — development
pip download --only-binary=:all: --python-version 3.11 \
  --dest hw_status/wheelhouse_dev \
  -r hw_status/hw_status/requirements-docker-dev.txt

# hw_proxy — development
pip download --only-binary=:all: --python-version 3.11 \
  --dest hw_proxy/wheelhouse_dev \
  -r hw_proxy/hw_proxy/requirements-docker-dev.txt
```

---

With this setup every artifact (Docker images, Python packages) is vendored locally and the
stack builds and runs without touching the Internet.
