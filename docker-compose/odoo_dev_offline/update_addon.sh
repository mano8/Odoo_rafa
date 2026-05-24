#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADDONS_SRC="$(realpath "${SCRIPT_DIR}/../../odoo_addons")"
ADDONS_DEST="${SCRIPT_DIR}/odoo/addons"

ADDONS=(
    pos_indv_receipt
    pos_json_printer
)

err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

[[ -d "$ADDONS_SRC" ]] || err "Source not found: $ADDONS_SRC"
[[ -d "$ADDONS_DEST" ]] || err "Destination not found: $ADDONS_DEST"

for addon in "${ADDONS[@]}"; do
    info "Syncing $addon..."
    rm -rf "${ADDONS_DEST:?}/${addon}"
    cp -R "${ADDONS_SRC}/${addon}" "${ADDONS_DEST}/${addon}"
done

info "Done. Restart Odoo to apply: docker compose restart fiesta_odoo"
