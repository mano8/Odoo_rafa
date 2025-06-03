#!/bin/bash
BACKUP_DIR="/opt/Odoo_rafa/backup"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/odoo_backup_$TIMESTAMP.tar.gz"

# Adjust volume or directory as needed
sudo docker run --rm -v odoo_pgdata:/volume -v "$BACKUP_DIR":/backup alpine \
    tar czf /backup/odoo_backup_$TIMESTAMP.tar.gz -C /volume .

echo "$BACKUP_FILE"