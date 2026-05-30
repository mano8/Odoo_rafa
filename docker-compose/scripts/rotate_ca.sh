#!/bin/bash
# MANUAL CA ROTATION — NOT to be automated or called by renew_certs.sh.
# Consequences:
#   - All clients lose trust until new CA is distributed
#   - Docker daemon must be restarted
#   - Browser CA must be manually re-imported on all client machines
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_DIR="${COMPOSE_DIR:-$REPO_DIR/docker-compose/odoo_prod}"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"
HOST_IP="${HOST_IP:-192.168.1.146}"
DOMAIN="${DOMAIN:-traefik-client.local}"
export CAROOT="/opt/Odoo_rafa/mkcert-ca"
DOCKER_SERVER_DIR="/etc/docker/certs"
DOCKER_CLIENT_DIR="$REPO_DIR/docker/certs"
TRAEFIK_CERT_DIR="$COMPOSE_DIR/traefik/certs"

cat <<WARN
=== CRITICAL: mkcert CA Rotation ===

This will:
  1. Delete the existing CA at $CAROOT
  2. Generate a new CA and install it in the system trust store
  3. Regenerate ALL TLS and mTLS certs
  4. RESTART the Docker daemon (brief service interruption)
  5. All client browsers must re-import the new CA

Clients that do NOT receive the new CA will see TLS errors immediately.

Type the word ROTATE to proceed, or Ctrl-C to abort:
WARN

read -r CONFIRMATION
[[ "$CONFIRMATION" == "ROTATE" ]] || { echo "Aborted."; exit 1; }

# Stop compose stack BEFORE removing the CA — avoids a window where Traefik
# holds the old cert while the CA is gone (TLS mismatch causes immediate errors).
echo "[rotate-ca] Stopping compose stack to prevent TLS mismatch window..."
docker compose -f "$COMPOSE_FILE" stop

echo "[rotate-ca] Removing existing CA..."
rm -f "$CAROOT/rootCA.pem" "$CAROOT/rootCA-key.pem"

echo "[rotate-ca] Generating new CA..."
mkdir -p "$CAROOT"
export CAROOT
mkcert -install

echo "[rotate-ca] Regenerating Traefik TLS cert..."
mkdir -p "$TRAEFIK_CERT_DIR"
mkcert \
    -cert-file "$TRAEFIK_CERT_DIR/local-cert.crt" \
    -key-file  "$TRAEFIK_CERT_DIR/local-cert.key" \
    "$DOMAIN" "localhost" "127.0.0.1" "$HOST_IP"

echo "[rotate-ca] Regenerating Docker mTLS certs..."
sudo mkdir -p "$DOCKER_SERVER_DIR"
sudo sh -c "CAROOT=$CAROOT mkcert \
    -cert-file $DOCKER_SERVER_DIR/server-cert.pem \
    -key-file  $DOCKER_SERVER_DIR/server-key.pem \
    docker-host.local 10.254.254.1 127.0.0.1"
mkdir -p "$DOCKER_CLIENT_DIR"
mkcert -client \
    -cert-file "$DOCKER_CLIENT_DIR/client-cert.pem" \
    -key-file  "$DOCKER_CLIENT_DIR/client-key.pem" \
    "docker-client"
sudo cp "$CAROOT/rootCA.pem" "$DOCKER_SERVER_DIR/ca.pem"
cp "$CAROOT/rootCA.pem" "$DOCKER_CLIENT_DIR/ca.pem"

echo "[rotate-ca] Restarting Docker daemon..."
sudo systemctl restart docker
echo "[rotate-ca] Waiting 15s for Docker to stabilise..."
sleep 15

docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

cat <<DONE
=== CA Rotation Complete ===

IMPORTANT: Distribute the new CA to all client machines:
  Cat the new CA:  cat $CAROOT/rootCA.pem

  Windows: double-click rootCA.pem → Install → Trusted Root Certification Authorities
  macOS:   sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain rootCA.pem
  Linux:   sudo cp rootCA.pem /usr/local/share/ca-certificates/odoo-rafa-ca.crt && sudo update-ca-certificates
DONE
