#!/usr/bin/env bash
# backup_volumes.sh — snapshot critical bind-mount volumes for disaster recovery.
#
# Backs up only business-critical data (PostgreSQL + Odoo filestore).
# Config, certs, and monitoring data are excluded — they are either tracked
# in git or can be regenerated.
#
# Usage: sudo bash backup_volumes.sh <COMPOSE_DIR> <BACKUP_DIR>
#
# Rotation: keeps the last MAX_BACKUPS snapshots; oldest is removed first.
# Expected compressed size: ~120 MB per snapshot.
#
# NOTE: BASE_UID (231072) must match auto_chown_volumes.sh and daemon.json.
set -euo pipefail
IFS=$'\n\t'

COMPOSE_DIR="${1:?Usage: $0 <COMPOSE_DIR> <BACKUP_DIR>}"
BACKUP_BASE="${2:-/opt/backups/odoo_rafa}"
MAX_BACKUPS=5

err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " >> $*"; }

[[ $EUID -ne 0 ]] && err "Run as root (sudo)."
[[ -d "$COMPOSE_DIR" ]] || err "COMPOSE_DIR not found: $COMPOSE_DIR"

# ── Rotation ──────────────────────────────────────────────────────────────────
mkdir -p "$BACKUP_BASE"
mapfile -t existing < <(find "$BACKUP_BASE" -maxdepth 1 -mindepth 1 -type d | sort)
while (( ${#existing[@]} >= MAX_BACKUPS )); do
    oldest="${existing[0]}"
    info "Rotating: removing oldest backup $(basename "$oldest")"
    rm -rf "$oldest"
    existing=("${existing[@]:1}")
done

# ── Destination ───────────────────────────────────────────────────────────────
DT=$(date +%Y-%m-%d_%H-%M-%S)
DEST="$BACKUP_BASE/$DT"
mkdir -p "$DEST"
info "Backup destination: $DEST"

# ── Stop DB and Odoo for a consistent pgdata snapshot (~30 s downtime) ────────
info "Stopping fiesta_db and fiesta_odoo..."
docker compose -f "$COMPOSE_DIR/docker-compose.yml" stop fiesta_db fiesta_odoo \
    || info "Warning: could not stop containers (may not be running) — continuing."

# ── Archive critical data ─────────────────────────────────────────────────────
info "Archiving postgres/pgdata..."
tar -czp -C "$COMPOSE_DIR/postgres" -f "$DEST/pgdata.tar.gz" pgdata

info "Archiving odoo/data (filestore)..."
tar -czp -C "$COMPOSE_DIR/odoo" -f "$DEST/odoo_data.tar.gz" data

# ── Restart containers ────────────────────────────────────────────────────────
info "Restarting fiesta_db and fiesta_odoo..."
docker compose -f "$COMPOSE_DIR/docker-compose.yml" start fiesta_db fiesta_odoo \
    || info "Warning: could not restart containers — start them manually."

# ── Manifest ─────────────────────────────────────────────────────────────────
{
    echo "Created:    $DT"
    echo "Source:     $COMPOSE_DIR"
    echo ""
    ls -lh "$DEST/"
} > "$DEST/MANIFEST.txt"

info "Backup complete:"
ls -lh "$DEST/"
