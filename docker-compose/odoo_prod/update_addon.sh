#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
ADDONS_SRC="/opt/Odoo_rafa/odoo_addons"
ADDONS_DEST="/opt/Odoo_rafa/docker-compose/odoo_prod/odoo/addons"
ODOO_UID=231172
ODOO_GID=231172

ADDONS=(
    pos_indv_receipt
    pos_json_printer
)

# --- Helpers ---
err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

# --- Validate root ---
[[ $EUID -ne 0 ]] && err "This script must be run as root."

for addon in "${ADDONS[@]}"; do
    info "Syncing $addon..."
    sudo rm -rf "${ADDONS_DEST}/${addon}"
    sudo cp -R "${ADDONS_SRC}/${addon}" "${ADDONS_DEST}/${addon}"
    sudo chown -R "${ODOO_UID}:${ODOO_GID}" "${ADDONS_DEST}/${addon}"
done

info "Done."
exit 0
