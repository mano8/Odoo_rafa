#!/bin/bash
# Output service statuses, one per line: <name> <type> <status>
# Used by hw_proxy GET /system/services/status

SYSTEMCTL=/usr/bin/systemctl
DOCKER=/usr/bin/docker

svc_status() {
    local name="$1"
    local status
    status=$("$SYSTEMCTL" is-active "${name}.service" 2>/dev/null) || status="inactive"
    echo "$name systemd $status"
}

ctr_status() {
    local name="$1"
    local container="$2"
    local status
    status=$("$DOCKER" inspect --format "{{.State.Status}}" "$container" 2>/dev/null) || status="not found"
    [[ -z "$status" ]] && status="not found"
    echo "$name docker $status"
}

svc_status "hw_proxy"
svc_status "odoo-pos"
svc_status "monitoring"
ctr_status "traefik"           "odoo_prod-traefik-1"
ctr_status "fiesta_db"         "odoo_prod-fiesta_db-1"
ctr_status "hw_status_service" "odoo_prod-hw_status_service-1"
ctr_status "fiesta_odoo"       "odoo_prod-fiesta_odoo-1"
ctr_status "grafana"           "monitoring-grafana-1"
ctr_status "prometheus"        "monitoring-prometheus-1"
