#!/usr/bin/env bash

set -euo pipefail

# === CONFIG ===
DOMAIN=${1:-traefik-client.local}     # Fallback domain
IP=${2:-192.168.1.146}                # Your local IP
CERT_NAME=${3:-local-cert}
DAYS_VALID=825

OUT_DIR="./traefik/certs"
mkdir -p "$OUT_DIR"

echo "[i] Generating local TLS cert for:"
echo "    - DOMAIN: $DOMAIN"
echo "    - IP:     $IP"
echo "    - Output: $OUT_DIR"

# === Generate a root CA (if not exists) ===
if [[ ! -f "$OUT_DIR/ca.key" ]]; then
  echo "[+] Generating root CA..."
  openssl genrsa -out "$OUT_DIR/ca.key" 4096
  openssl req -x509 -new -nodes -key "$OUT_DIR/ca.key" \
    -sha256 -days $DAYS_VALID -out "$OUT_DIR/ca.crt" \
    -subj "/C=ES/ST=Local/L=LAN/O=LocalCA/CN=Local Dev CA"
else
  echo "[=] Root CA already exists: $OUT_DIR/ca.crt"
fi

# === Create OpenSSL config with SAN ===
CONFIG="$OUT_DIR/$CERT_NAME.conf"
cat > "$CONFIG" <<EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[dn]
C=ES
ST=Local
L=LAN
O=LocalDev
CN=$DOMAIN

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
IP.1  = 127.0.0.1
IP.2  = $IP
EOF

# === Generate private key and CSR ===
echo "[+] Generating key and CSR..."
openssl genrsa -out "$OUT_DIR/$CERT_NAME.key" 2048

openssl req -new -key "$OUT_DIR/$CERT_NAME.key" \
  -out "$OUT_DIR/$CERT_NAME.csr" -config "$CONFIG"

# === Sign cert with CA ===
echo "[+] Signing certificate with local CA..."
openssl x509 -req -in "$OUT_DIR/$CERT_NAME.csr" \
  -CA "$OUT_DIR/ca.crt" -CAkey "$OUT_DIR/ca.key" \
  -CAcreateserial -out "$OUT_DIR/$CERT_NAME.crt" \
  -days $DAYS_VALID -sha256 -extfile "$CONFIG" -extensions req_ext

# === Output PEM and PFX ===
cat "$OUT_DIR/$CERT_NAME.key" "$OUT_DIR/$CERT_NAME.crt" > "$OUT_DIR/$CERT_NAME.pem"

openssl pkcs12 -export \
  -out "$OUT_DIR/$CERT_NAME.pfx" \
  -inkey "$OUT_DIR/$CERT_NAME.key" \
  -in "$OUT_DIR/$CERT_NAME.crt" \
  -certfile "$OUT_DIR/ca.crt" \
  -passout pass:

echo "[✔] Certificate files created in: $OUT_DIR"

# === Optional: Add to /etc/hosts ===
if grep -qv "$DOMAIN" /etc/hosts && [[ "$DOMAIN" != "$IP" ]]; then
  echo "[+] Adding $DOMAIN to /etc/hosts..."
  echo "$IP $DOMAIN" | sudo tee -a /etc/hosts
else
  echo "[=] Domain already in /etc/hosts or not needed."
fi

echo "[✅] Done. You can now configure Traefik or your FastAPI app with:"
echo "     - Cert: $OUT_DIR/$CERT_NAME.crt"
echo "     - Key:  $OUT_DIR/$CERT_NAME.key"
echo "     - CA:   $OUT_DIR/ca.crt (trust it in browser/system)"

exit 0