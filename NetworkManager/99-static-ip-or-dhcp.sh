#!/bin/bash

# Dispatcher script to apply static IP on specific subnet (192.168.1.0/24)
# Otherwise, fallback to DHCP

IFACE="$1"
STATUS="$2"

# Only act on wired interface
TARGET_IFACE="enp5s0"
CON_NAME="Wired connection 1"

STATIC_IP="192.168.1.146/24"
STATIC_GW="192.168.1.1"
DNS_SERVERS="1.1.1.1 8.8.8.8"
TARGET_SUBNET="192.168.1.0/24"

log() {
    logger -t static-ip "$1"
}

wait_for_gateway() {
    local timeout=5
    for _ in $(seq 1 "$timeout"); do
        GW=$(ip route | grep "^default" | grep "$IFACE" | awk '{print $3}')
        [[ -n "$GW" ]] && break
        sleep 1
    done
    echo "$GW"
}

is_gateway_in_subnet() {
    local gw_ip="$1"
    ipcalc -c "$gw_ip" "$TARGET_SUBNET" >/dev/null 2>&1
    return $?
}

# Skip interfaces we don’t care about
if [ "$IFACE" != "$TARGET_IFACE" ]; then
    log "Skipped: Interface $IFACE is not $TARGET_IFACE"
    exit 0
fi

if [ "$STATUS" = "up" ]; then
    GW=$(wait_for_gateway)

    if [[ -z "$GW" ]]; then
        log "No gateway found for $IFACE. Reverting to DHCP"
        nmcli con modify "$CON_NAME" ipv4.method auto
        nmcli con up "$CON_NAME"
        exit 0
    fi

    if is_gateway_in_subnet "$GW"; then
        log "Detected subnet $TARGET_SUBNET. Setting static IP $STATIC_IP on $IFACE"

        nmcli con modify "$CON_NAME" \
            ipv4.addresses "$STATIC_IP" \
            ipv4.gateway "$STATIC_GW" \
            ipv4.dns "$DNS_SERVERS" \
            ipv4.method manual \
            ipv4.ignore-auto-routes yes \
            ipv4.ignore-auto-dns yes
    else
        log "Gateway $GW is not in $TARGET_SUBNET. Reverting to DHCP on $IFACE"

        nmcli con modify "$CON_NAME" \
            ipv4.method auto \
            ipv4.dns "" \
            ipv4.addresses "" \
            ipv4.gateway "" \
            ipv4.ignore-auto-routes no \
            ipv4.ignore-auto-dns no
    fi

    nmcli con up "$CON_NAME"
fi