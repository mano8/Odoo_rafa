# Offline Mode

When you need to run the entire **Fiesta POS** stack with **no Internet** (e.g. in an air-gapped environment), you must:

1. **Vendor all Docker images** locally (Traefik, Postgres, Odoo, Python-fat)
2. **Cache all Python wheels** in `hw_status/wheelhouse/` and `hw_status/wheelhouse_dev/`
3. **Configure** Compose and Dockerfiles to install **only** from those local artifacts

---

## Repository Layout

```text
/opt/Odoo_rafa/
├── docker_offline/             ← offline-prep artifacts & Makefiles
│   ├── Makefile.prepare        ← pull → build → save (tarballs)
│   ├── Makefile.update         ← save → load → (optional compose up)
│   ├── Makefile.wheels         ← generate wheelhouse dirs
│   ├── python-3.11-slim.tar
│   ├── traefik_v3.4.0.tar
│   ├── postgres_13.21-alpine3.20.tar
│   ├── odoo_18.0.tar
│   ├── python-3.11-fat.tar
│   ├── prometheus_v3.4.0.tar
│   └── grafana_12.0.1.tar
├── hw_proxy/
│   ├── wheelhouse_dev/         ← dev wheels (in `.gitignore`)
│   └── hw_proxy/
│       ├── requirements-docker-dev.txt
│       └── Dockerfile.offline.dev  ← builds using local wheelhouse (dev)
└── hw_status/
    ├── wheelhouse/             ← prod wheels (in `.gitignore`)
    ├── wheelhouse_dev/         ← dev wheels (in `.gitignore`)
    └── hw_status/
        ├── requirements-docker.txt
        ├── requirements-docker-dev.txt
        ├── Dockerfile.fat          ← Vendor Docker hw_status base image
        ├── Dockerfile.offline.dev  ← builds using local wheelhouses (dev)
        └── Dockerfile.offline      ← builds using local wheelhouses (prod)
```

---

## 1. Prepare offline artifacts (online workstation)

1. **Docker images**

   ```bash
   cd /opt/Odoo_rafa/docker_offline
   make -f Makefile.prepare
   ```

   * Pulls Traefik, Postgres, Odoo, builds `python-3.11-fat`, and saves them to `*.tar`

2. **Python wheels**

   ```bash
   cd /opt/Odoo_rafa/docker_offline
   make -f Makefile.wheels prod     # fills wheelhouse/
   # And/Or
   make -f Makefile.wheels dev      # fills wheelhouse_dev/
   ```

---

## 2. Load & run offline (air-gapped host)

Copy the entire `/opt/Odoo_rafa/` directory (including `docker_offline/*.tar` and both `wheelhouse*`) to the target host, then:

```bash
cd /opt/Odoo_rafa/docker_offline
make -f Makefile.update load
```

`make -f Makefile.update load` does:

1. Loads each `*.tar` via `docker load -i ...`

---

## 3. Run with Internet (online workstation)

You can also skip copying `.tar` and wheels manually if you're online:

```bash
# Python wheels
cd /opt/Odoo_rafa/docker_offline
make -f Makefile.wheels prod
# And/Or
make -f Makefile.wheels dev

# Docker images
cd /opt/Odoo_rafa/docker_offline
make -f Makefile.update
```

`make -f Makefile.update` does:

1. Pull images
2. Build `python-3.11-fat`
3. Save all to `.tar`
4. Load into Docker

---

## 4. Manual fallback commands

### Docker images

```bash
cd /opt/Odoo_rafa/docker_offline

docker pull python:3.11-slim
docker pull traefik:v3.4.0
docker pull postgres:13.21-alpine3.20
docker pull odoo:18.0
docker pull prom/prometheus:v3.4.0
docker pull grafana/grafana:12.0.1

docker build -f ../hw_status/hw_status/Dockerfile.fat -t my-python-3.11-fat:latest ../hw_status/hw_status

docker save python:3.11-slim            -o python-3.11-slim.tar
docker save traefik:v3.4.0              -o traefik_v3.4.0.tar
docker save postgres:13.21-alpine3.20   -o postgres_13.21-alpine3.20.tar
docker save odoo:18.0                   -o odoo_18.0.tar
docker save my-python-3.11-fat:latest   -o python-3.11-fat.tar
docker save prom/prometheus:v3.4.0      -o prometheus_v3.4.0.tar
docker save grafana/grafana:12.0.1      -o grafana_12.0.1.tar

# On offline host:
docker load -i python-3.11-slim.tar
docker load -i traefik_v3.4.0.tar
docker load -i postgres_13.21-alpine3.20.tar
docker load -i odoo_18.0.tar
docker load -i python-3.11-fat.tar
docker load -i prometheus_v3.4.0.tar
docker load -i grafana_12.0.1.tar
```

### Python wheels

```bash
# hw_status — production wheels:
pip download --dest hw_status/wheelhouse     -r hw_status/hw_status/requirements-docker.txt

# hw_status — development wheels:
pip download --dest hw_status/wheelhouse_dev -r hw_status/hw_status/requirements-docker-dev.txt

# hw_proxy — development wheels:
pip download --dest hw_proxy/wheelhouse_dev  -r hw_proxy/hw_proxy/requirements-docker-dev.txt
```

---

With this setup, **every** piece (OS packages, images, Python libs) lives in your repo and can be built, loaded, and run **without** touching the Internet.
