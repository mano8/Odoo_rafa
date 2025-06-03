#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
SOURCE="/opt/Odoo_rafa/odoo_addons/pos_indv_receipt"
DEST="/opt/Odoo_rafa/docker-compose/odoo_addon/odoo/addons/pos_indv_receipt"

# --- Helpers ---
err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

# --- Validate root ---
[[ $EUID -ne 0 ]] && err "This script must be run as root."

info "Remove current pos_individual_product_receipts addon files."
sudo rm -r "$DEST" || true

info "Copy new current pos_individual_product_receipts addon files."
sudo cp -R "$SOURCE" "$DEST"

info "Set owner"
sudo chown -R 231172:231172 "$DEST"

exit 0
