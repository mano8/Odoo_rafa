#!/usr/bin/env bash
set -euo pipefail

# --- Helpers ---
err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

# --- Validate root ---
[[ $EUID -ne 0 ]] && err "This script must be run as root."

info "Preparing docker compose environment..."

if ! ./generate_odoo_conf.sh; then
    err "Unable to generate Odoo configuration file."
fi

if ! ./auto_chown_volumes.sh; then
    err "Unable to generate Odoo configuration file."
fi

info "Docker compose environment is ready..."
exit 0
# --- End of script ---