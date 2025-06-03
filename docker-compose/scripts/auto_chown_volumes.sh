#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# --- Resolve Compose project root (where you run the script from) ---
PROJECT_ROOT="$PWD"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

[[ -f "$COMPOSE_FILE" ]] || {
  echo "ERROR: No docker-compose.yml found in $PROJECT_ROOT" >&2
  exit 1
}

# --- Config ---
BASE_UID=231072
BASE_GID=231072

# --- Predefined internal UIDs for services (from inside container) ---
declare -A SERVICES_MAP=(
  [fiesta_odoo]="fiesta_odoo"
  [fiesta_db]="fiesta_db"
  [traefik]="traefik"
)

declare -A SERVICE_UID_MAP=(
  [fiesta_odoo]=100
  [fiesta_db]=0
  [traefik]=0
)

declare -A ODOO_VOLUMES_MAP=(
  [addons]="$PROJECT_ROOT/odoo/addons"
  [conf]="$PROJECT_ROOT/odoo/config"
  [data]="$PROJECT_ROOT/odoo/data"
)

declare -A DB_VOLUMES_MAP=(
  [pgdata]="$PROJECT_ROOT/postgres/pgdata"
)

declare -A TRAEFIK_VOLUMES_MAP=(
  [certs]="$PROJECT_ROOT/traefik/certs"
)

# --- Helpers ---
err()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo " * $*"; }

# --- Validate root ---
[[ $EUID -ne 0 ]] && err "This script must be run as root."

# --- Args ---
ENVIRONMENT="${1:-prod}"
USER_DEV="${2:-}"

[[ "$ENVIRONMENT" == "dev" || "$ENVIRONMENT" == "prod" ]] || \
  err "ENVIRONMENT must be 'dev' or 'prod'"

if [[ "$ENVIRONMENT" == "dev" ]]; then
  [[ -n "$USER_DEV" ]] || err "In dev mode, USER_DEV must be specified as second argument"
  id "$USER_DEV" >/dev/null 2>&1 || err "User '$USER_DEV' does not exist"
  DEV_GID=$(id -g "$USER_DEV")
fi

info "Preparing volumes with userns-remap..."
info "Environment: $ENVIRONMENT"
[[ "$ENVIRONMENT" == "dev" ]] && info "Dev User: $USER_DEV"
info "Compose project root: $PROJECT_ROOT"


# --- Main loop ---
info "Start auto chown for services:"
for service in "${!SERVICES_MAP[@]}"; do
  info " * service: $service"

  internal_uid="${SERVICE_UID_MAP[$service]:-}"
  if [[ -z "$internal_uid" ]]; then
    info "  * No UID mapping for $service — skipping"
    continue
  fi

  info "  * internal UID : $internal_uid"

  host_uid=$((BASE_UID + internal_uid))
  host_gid=$((BASE_GID + internal_uid))
  
  info "  * host UID:GID : $host_uid:$host_gid"
  if [[ "$service" == "fiesta_odoo" ]]; then
    volumes=("${ODOO_VOLUMES_MAP[@]}")
  elif [[ "$service" == "fiesta_db" ]]; then
    volumes=("${DB_VOLUMES_MAP[@]}")
  elif [[ "$service" == "traefik" ]]; then
    volumes=("${TRAEFIK_VOLUMES_MAP[@]}")
  else
    info "  * No volume mapping for $service — skipping"
    continue
  fi
  
  if [[ -z "$volumes" ]]; then
    info "  * No bind mounts found for $service — skipping"
    continue
  fi
  for vol in "${volumes[@]}"; do
    info "  * Current Volume: $vol"
    abs_path="$(realpath "$vol" 2>/dev/null || echo "$vol")"

    info "  * Ensuring directory exists: $abs_path"
    if [[ ! -d "$abs_path" ]]; then
      info "  * Directory does not exist, creating: $abs_path"
      mkdir -p "$abs_path" || err "Failed to create directory $abs_path"
    fi
    if [[ "$ENVIRONMENT" == "dev" ]]; then
      info "  * Chown to UID:GID $host_uid:$DEV_GID (read/write for $USER_DEV)"
      chown -R "$host_uid:$DEV_GID" "$abs_path"
      chmod -R g+rw "$abs_path"
    else
      info "  * Chown to UID:GID $host_uid:$host_gid"
      chown -R "$host_uid:$host_gid" "$abs_path"
    fi
  done
done


info "Volume ownership updated successfully."
exit 0