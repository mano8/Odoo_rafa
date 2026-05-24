#!/bin/bash
set -euo pipefail

BACKUP_DIR="/opt/Odoo_rafa/backup"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/odoo_backup_$TIMESTAMP.sql.gz"

DB_CONTAINER="${DB_CONTAINER:-fiesta_db}"
DB_USER="${DB_USER:-odoo}"
DB_DATABASE="${DB_DATABASE:-odoo}"

docker exec "$DB_CONTAINER" \
    pg_dump -U "$DB_USER" "$DB_DATABASE" | gzip > "$BACKUP_FILE"

echo "$BACKUP_FILE"
