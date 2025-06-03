#!/usr/bin/env bash
set -euo pipefail

# --- Paths ---
EXAMPLE_CONF="./odoo.conf.example"
TARGET_DIR="./odoo/config"
TARGET_CONF="$TARGET_DIR/odoo.conf"
ENV_FILE="./.env"

# --- Helpers ---
err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

# --- Validate root ---
[[ $EUID -ne 0 ]] && err "This script must be run as root."

# --- Load .env ---
if [ -f "$ENV_FILE" ]; then
    info "[INFO] Loading environment variables from $ENV_FILE"
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
else
    err ".env file not found!"
fi

# --- Ensure target dir exists ---
sudo mkdir -p "$TARGET_DIR"

# --- Copy example config ---
cp "$EXAMPLE_CONF" "$TARGET_CONF"
info "[INFO] Copied $EXAMPLE_CONF to $TARGET_CONF"

# --- Replace values ---
sed -i \
    -e "s/^db_host *=.*/db_host = ${DB_HOST}/" \
    -e "s/^db_port *=.*/db_port = 5432/" \
    -e "s/^db_user *=.*/db_user = ${DB_USER}/" \
    -e "s/^db_password *=.*/db_password = \"${DB_PASSWORD}\"/" \
    -e "s/^db_name *=.*/db_name = ${DB_DATABASE}/" \
    "$TARGET_CONF"

info "[INFO] Updated odoo.conf with .env values:"
info "       - db_host: $DB_HOST"
info "       - db_user: $DB_USER"
info "       - db_password: [REDACTED]"
info "       - db_name: $DB_DATABASE"

exit 0