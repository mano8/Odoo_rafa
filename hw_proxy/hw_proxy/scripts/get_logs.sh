#!/bin/bash
# Fetch service logs filtered by level.
# Usage: get_logs.sh <service> <lines> <level>
# level: error | warning | info | all

JOURNALCTL=/usr/bin/journalctl
SERVICE="${1:-hw_proxy}"
LINES="${2:-100}"
LEVEL="${3:-warning}"

case "$LEVEL" in
    error)   PRIORITY=err ;;
    info)    PRIORITY=info ;;
    all)     PRIORITY="" ;;
    *)       PRIORITY=warning ;;
esac

systemd_logs() {
    local unit="${1}.service"
    if [[ -n "$PRIORITY" ]]; then
        "$JOURNALCTL" -u "$unit" -n "$LINES" -p "$PRIORITY" --no-pager --output=short-iso
    else
        "$JOURNALCTL" -u "$unit" -n "$LINES" --no-pager --output=short-iso
    fi
}

# All docker output enters journald at INFO priority when using the journald log driver.
# For filtered levels, grep by keyword to surface important lines.
docker_logs() {
    local container="$1"
    if [[ "$LEVEL" == "all" ]]; then
        "$JOURNALCTL" CONTAINER_NAME="$container" -n "$LINES" --no-pager --output=short-iso
    else
        "$JOURNALCTL" CONTAINER_NAME="$container" -n "$LINES" --no-pager --output=short-iso | \
            grep -iE "(error|warn|critical|fatal|exception|traceback)" || true
    fi
}

case "$SERVICE" in
    hw_proxy)           systemd_logs "hw_proxy" ;;
    odoo-pos)           systemd_logs "odoo-pos" ;;
    monitoring)         systemd_logs "monitoring" ;;
    traefik)            docker_logs "odoo_prod-traefik-1" ;;
    fiesta_db)          docker_logs "odoo_prod-fiesta_db-1" ;;
    hw_status_service)  docker_logs "odoo_prod-hw_status_service-1" ;;
    fiesta_odoo)        docker_logs "odoo_prod-fiesta_odoo-1" ;;
    grafana)            docker_logs "monitoring-grafana-1" ;;
    prometheus)         docker_logs "monitoring-prometheus-1" ;;
    *)                  echo "[Unknown service: $SERVICE]" ;;
esac
