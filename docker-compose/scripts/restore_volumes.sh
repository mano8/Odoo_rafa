#!/usr/bin/env bash
# restore_volumes.sh — restore critical volumes from a backup snapshot.
#
# Restores PostgreSQL data and Odoo filestore from a backup created by
# backup_volumes.sh.  Container lifecycle (stop/start) is managed by the
# calling Makefile target, not here.
#
# Usage: sudo bash restore_volumes.sh <COMPOSE_DIR> <BACKUP_PATH>
#
# NOTE: BASE_UID (231072) must match auto_chown_volumes.sh and daemon.json.
set -euo pipefail
IFS=$'\n\t'

COMPOSE_DIR="${1:?Usage: $0 <COMPOSE_DIR> <BACKUP_PATH>}"
BACKUP_PATH="${2:?Usage: $0 <COMPOSE_DIR> <BACKUP_PATH>}"
SCRIPTS_DIR="$(dirname "$0")"

err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " >> $*"; }

[[ $EUID -ne 0 ]]           && err "Run as root (sudo)."
[[ -d "$BACKUP_PATH" ]]     || err "Backup path not found: $BACKUP_PATH"
[[ -d "$COMPOSE_DIR" ]]     || err "COMPOSE_DIR not found: $COMPOSE_DIR"

for f in pgdata.tar.gz odoo_data.tar.gz; do
    [[ -f "$BACKUP_PATH/$f" ]] || err "Missing archive: $BACKUP_PATH/$f"
done

info "Restoring from: $BACKUP_PATH"

# ── pgdata: remove existing, then extract clean ───────────────────────────────
# A clean extract ensures no stale WAL or temp files from the old instance.
info "Restoring postgres/pgdata (clean extract)..."
rm -rf "$COMPOSE_DIR/postgres/pgdata"
mkdir -p "$COMPOSE_DIR/postgres"
tar -xzp -C "$COMPOSE_DIR/postgres" -f "$BACKUP_PATH/pgdata.tar.gz"

# ── Odoo filestore: clean extract ────────────────────────────────────────────
info "Restoring odoo/data (filestore, clean extract)..."
rm -rf "$COMPOSE_DIR/odoo/data"
mkdir -p "$COMPOSE_DIR/odoo"
tar -xzp -C "$COMPOSE_DIR/odoo" -f "$BACKUP_PATH/odoo_data.tar.gz"

# ── Fix ownership (safety net for userns-remap) ───────────────────────────────
info "Fixing volume ownership (userns-remap)..."
cd "$COMPOSE_DIR"
bash "$SCRIPTS_DIR/auto_chown_volumes.sh" prod

info "Restore complete. Start the stack with: make up"
