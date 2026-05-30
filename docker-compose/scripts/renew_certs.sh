#!/bin/bash
# Certificate renewal using mkcert.
# Usage:
#   renew_certs.sh              auto-renew if expiring within THRESHOLD days
#   renew_certs.sh --status     show expiry only, no changes
#   renew_certs.sh --force      renew regardless of expiry
# CA rotation is a separate operation: rotate_ca.sh (interactive, manual only)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_DIR="${COMPOSE_DIR:-$REPO_DIR/docker-compose/odoo_prod}"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"
HOST_IP="${HOST_IP:-192.168.1.146}"
DOMAIN="${DOMAIN:-traefik-client.local}"
THRESHOLD="${THRESHOLD:-30}"

export CAROOT="/opt/Odoo_rafa/mkcert-ca"
TRAEFIK_CERT_DIR="$COMPOSE_DIR/traefik/certs"
DOCKER_SERVER_DIR="/etc/docker/certs"
DOCKER_CLIENT_DIR="$REPO_DIR/docker/certs"

MODE="check"
for arg in "$@"; do
    case "$arg" in
        --status) MODE="status" ;;
        --force)  MODE="force"  ;;
    esac
done

_days_until_expiry() {
    local cert="$1"
    [[ -f "$cert" ]] || { echo "-999"; return; }
    local end
    end=$(openssl x509 -noout -enddate -in "$cert" 2>/dev/null | cut -d= -f2) \
        || { echo "-999"; return; }
    [[ -z "$end" ]] && { echo "-999"; return; }
    local end_epoch now_epoch
    end_epoch=$(date -d "$end" +%s 2>/dev/null) || { echo "-999"; return; }
    now_epoch=$(date +%s)
    echo $(( (end_epoch - now_epoch) / 86400 ))
}

_cert_state() {
    local days="$1"
    if   [[ "$days" -le -999 ]]; then echo "MISSING"
    elif [[ "$days" -lt 0    ]]; then echo "EXPIRED"
    elif [[ "$days" -lt "$THRESHOLD" ]]; then echo "EXPIRING"
    else echo "OK"
    fi
}

labels=("Traefik TLS" "Docker mTLS CA" "Docker mTLS Client")
certs=(
    "$TRAEFIK_CERT_DIR/local-cert.crt"
    "$DOCKER_SERVER_DIR/ca.pem"
    "$DOCKER_CLIENT_DIR/client-cert.pem"
)

echo "=== Certificate Status (threshold: ${THRESHOLD}d, CAROOT=$CAROOT) ==="
for i in "${!labels[@]}"; do
    days=$(_days_until_expiry "${certs[$i]}")
    state=$(_cert_state "$days")
    printf "  %-22s %-10s (%s days)\n" "${labels[$i]}" "$state" "$days"
done
echo ""

[[ "$MODE" == "status" ]] && exit 0

_ensure_ca() {
    [[ -f "$CAROOT/rootCA.pem" ]] || {
        echo "[mkcert] No CA found at $CAROOT — creating new CA..."
        mkdir -p "$CAROOT"
        export CAROOT
        mkcert -install
    }
}

_renew_traefik_tls() {
    echo "[mkcert] Renewing Traefik TLS cert for $DOMAIN / $HOST_IP..."
    mkdir -p "$TRAEFIK_CERT_DIR"
    mkcert \
        -cert-file "$TRAEFIK_CERT_DIR/local-cert.crt" \
        -key-file  "$TRAEFIK_CERT_DIR/local-cert.key" \
        "$DOMAIN" "localhost" "127.0.0.1" "$HOST_IP"
    echo "[renew] Restarting Traefik..."
    docker compose -f "$COMPOSE_FILE" restart traefik
    echo "[renew] Traefik TLS renewed."
}

_renew_docker_leaf() {
    echo "[mkcert] Renewing Docker mTLS leaf certs..."
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
    echo "[renew] Restarting Traefik to pick up new client certs..."
    docker compose -f "$COMPOSE_FILE" restart traefik
    echo "[renew] Docker mTLS renewed."
}

traefik_days=$(_days_until_expiry "${certs[0]}")
docker_days=$(_days_until_expiry "${certs[2]}")
traefik_state=$(_cert_state "$traefik_days")
docker_state=$(_cert_state "$docker_days")

_ensure_ca

case "$MODE" in
    force)
        _renew_traefik_tls
        _renew_docker_leaf
        ;;
    check)
        [[ "$traefik_state" != "OK" ]] \
            && _renew_traefik_tls \
            || echo "[check] Traefik TLS OK ($traefik_days days) — skipping"
        [[ "$docker_state" != "OK" ]] \
            && _renew_docker_leaf \
            || echo "[check] Docker mTLS OK ($docker_days days) — skipping"
        ;;
esac

echo "=== Done ==="
