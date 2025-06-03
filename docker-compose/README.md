# Docker compose

## Offline mode

In case plan to use this, without internet conexion, you need to ensure docker images are available offline.

To guarantee that your entire stack can be built and brought up without any Internet access, you’ll need to:

 1. Vendor all Docker images locally (Traefik, Postgres, Odoo)
 2. Bundle your Python dependencies into a local wheel cache
 3. Adjust your Compose and Dockerfile to pull from your local sources

### Pre-pull & save your base images

```bash
# create directory to store images
mkdir -p -R /opt/Odoo_rafa/docker_offline
cd /opt/Odoo_rafa/docker_offline

# Pull the images you depend on
sudo docker pull traefik:v3.4.0
sudo docker pull postgres:13.21-alpine3.20
sudo docker pull odoo:18.0

# Save them to tar files
sudo docker save traefik:v3.4.0 -o traefik_v3.4.0.tar
sudo docker save postgres:13.21-alpine3.20 -o postgres_13.21-alpine3.20.tar
sudo docker save odoo:18.0  -o odoo_18.0.tar

# Load for offline use
sudo docker load -i traefik_v3.4.0.tar
sudo docker load -i postgres_13.21-alpine3.20.tar
sudo docker load -i odoo_18.0.tar
```

#### `hw_proxy_service` container

This container have a Dockerfile that's need by default internet conexion to install needed packages to work.

1. Save base image

```bash
# Build and save
sudo docker build -f Dockerfile.fat -t python-3.11-fat:latest .
sudo docker save python-3.11-fat:latest -o python-3.11-fat.tar
# Load for offline use
sudo docker load -i python-3.11-fat.tar
```

2. Save python packages

Needed python packages must be downloaded and stored.

```bash
cd /opt/Odoo_rafa/hw_proxy

# create directory to store prod python packages
mkdir /opt/Odoo_rafa/hw_proxy/wheelhouse
# Download and save python packages
pip download --dest wheelhouse -r hw_proxy/requirements-docker.txt


# create directory to store dev python packages
mkdir /opt/Odoo_rafa/hw_proxy/wheelhouse_dev
# Download and save python packages
pip download --dest wheelhouse_dev -r hw_proxy/requirements-docker-dev.txt
```



Two Docker files are available  for that purpose for dev/prod use cases:

- **`hw_proxy/hw_proxy/Dockerfile.offline`**: Prod 

To enable possiblity to work offline who need prebuild an image, and download needed python packages



## 