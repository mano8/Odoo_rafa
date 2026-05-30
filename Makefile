# ==============================================================================
# Odoo POS Stack — Deployment Makefile
#
# Usage:  make help
# Requires sudo privileges for most targets.
# Designed to run on the Linux deployment machine from /opt/Odoo_rafa.
# ==============================================================================

REPO_DIR       := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
COMPOSE_DIR    := $(REPO_DIR)/docker-compose/odoo_prod
MONITORING_DIR := $(REPO_DIR)/docker-compose/monitoring
SCRIPTS_DIR    := $(REPO_DIR)/docker-compose/scripts
SERVICES_DIR   := $(REPO_DIR)/services/odoo_server
DOCKER_SCRIPTS := $(REPO_DIR)/docker/scripts

# Overridable at the command line, e.g.: make install HW_USER=myuser
SUDO      ?= sudo
HW_USER   ?= hw_user
HOST_IP   ?= 192.168.1.146
DOMAIN    ?= traefik-client.local
CERT_NAME ?= local-cert
# Set OFFLINE=1 to vendor wheels and load image tarballs before building.
# e.g.: make stack-up OFFLINE=1
OFFLINE    ?= 0
BACKUP_DIR ?= /opt/backups/odoo_rafa

.DEFAULT_GOAL := help

.PHONY: help check install \
        install-user install-sudoers install-firewall install-systemd \
        certs-traefik certs-docker \
        deploy-hw-proxy update-hw-proxy update-odoo-addon volumes build \
        create-networks stack-up up down restart update \
        monitoring-up monitoring-down monitoring-logs \
        monitoring-reload monitoring-reload-prometheus monitoring-reload-grafana \
        logs status backup backup-volumes restore-volumes

# ──────────────────────────────────────────────────────────────────────────────
help:
	@printf "\n\033[1mOdoo POS Stack\033[0m\n\n"
	@printf "\033[4mFirst-time setup\033[0m (all targets are idempotent):\n"
	@printf "  %-26s %s\n" "make install"           "Full fresh-machine setup"
	@printf "  %-26s %s\n" "make install-user"       "Create hw_user, add to dialout/lp"
	@printf "  %-26s %s\n" "make install-sudoers"    "Grant hw_user reboot/shutdown rights"
	@printf "  %-26s %s\n" "make install-firewall"   "Configure ufw rules for ports 9000-9002"
	@printf "  %-26s %s\n" "make certs-traefik"      "Generate Traefik TLS certificates"
	@printf "  %-26s %s\n" "make certs-docker"       "Generate Docker mTLS certificates"
	@printf "  %-26s %s\n" "make deploy-hw-proxy"    "Deploy hw_proxy service (venv + code)"
	@printf "  %-26s %s\n" "make update-hw-proxy"    "Pull main, redeploy hw_proxy, restart service"
	@printf "  %-26s %s\n" "make update-odoo-addon"  "Run addon update script and restart Odoo container"
	@printf "  %-26s %s\n" "make install-systemd"    "Install and enable systemd services"
	@printf "  %-26s %s\n" "make volumes"            "Fix Docker volume ownership (userns-remap)"
	@printf "  %-26s %s\n" "make build"              "Build Docker images"
	@printf "\n\033[4mRuntime\033[0m:\n"
	@printf "  %-26s %s\n" "make stack-up"           "Rebuild images, start odoo_prod + monitoring (add OFFLINE=1 for air-gapped)"
	@printf "  %-26s %s\n" "make up"                 "Start odoo_prod + monitoring (no rebuild)"
	@printf "  %-26s %s\n" "make down"               "Stop the odoo_prod stack"
	@printf "  %-26s %s\n" "make restart"            "Restart odoo_prod + monitoring"
	@printf "  %-26s %s\n" "make update"             "Pull code, redeploy hw_proxy, rebuild"
	@printf "  %-26s %s\n" "make monitoring-up"               "Start only the monitoring stack (Prometheus + Grafana)"
	@printf "  %-26s %s\n" "make monitoring-down"             "Stop only the monitoring stack"
	@printf "  %-26s %s\n" "make monitoring-logs"             "Follow monitoring container logs"
	@printf "  %-26s %s\n" "make monitoring-reload"           "Reload Prometheus config (SIGHUP) + restart Grafana"
	@printf "  %-26s %s\n" "make monitoring-reload-prometheus" "Reload prometheus.yml with no downtime (SIGHUP)"
	@printf "  %-26s %s\n" "make monitoring-reload-grafana"   "Restart Grafana to apply provisioning changes"
	@printf "  %-26s %s\n" "make logs"               "Follow odoo_prod container logs"
	@printf "  %-26s %s\n" "make status"             "Show status of all services and containers"
	@printf "\n\033[4mMaintenance\033[0m:\n"
	@printf "  %-26s %s\n" "make backup"             "Trigger PostgreSQL database backup"
	@printf "  %-26s %s\n" "make backup-volumes"     "Snapshot pgdata + filestore to BACKUP_DIR (max 5, rotated)"
	@printf "  %-26s %s\n" "make restore-volumes"    "Restore from snapshot: make restore-volumes BACKUP=<path>"
	@printf "  %-26s %s\n" "make check"              "Verify prerequisites"
	@printf "\n\033[4mOverridable variables\033[0m:\n"
	@printf "  HW_USER=%-18s Hardware service user  (current: $(HW_USER))\n" ""
	@printf "  HOST_IP=%-18s Host LAN IP            (current: $(HOST_IP))\n" ""
	@printf "  DOMAIN=%-19s Traefik domain          (current: $(DOMAIN))\n\n" ""

# ──────────────────────────────────────────────────────────────────────────────
# Prerequisite check
# ──────────────────────────────────────────────────────────────────────────────
check:
	@echo "[check] Verifying prerequisites..."
	@command -v docker  >/dev/null 2>&1 || { echo "ERROR: docker not installed";  exit 1; }
	@command -v openssl >/dev/null 2>&1 || { echo "ERROR: openssl not installed"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not installed"; exit 1; }
	@command -v rsync   >/dev/null 2>&1 || { echo "ERROR: rsync not installed";   exit 1; }
	@command -v ufw     >/dev/null 2>&1 || { echo "ERROR: ufw not installed";     exit 1; }
	@echo "[check] All prerequisites satisfied."

# ──────────────────────────────────────────────────────────────────────────────
# Full install — safe to re-run on an existing machine
#
# NOTE: copy and edit .env files before running 'make up':
#   cp $(COMPOSE_DIR)/env.example.txt $(COMPOSE_DIR)/.env
#   cp $(REPO_DIR)/hw_proxy/hw_proxy/en.example.txt /opt/hw_proxy/hw_proxy/.env
# ──────────────────────────────────────────────────────────────────────────────
install: check install-user install-sudoers install-firewall \
         certs-traefik deploy-hw-proxy install-systemd create-networks volumes build
	@echo ""
	@echo "================================================================"
	@echo " Install complete. Before starting the stack:"
	@echo ""
	@echo "  1. Edit the Compose environment:"
	@echo "       cp $(COMPOSE_DIR)/env.example.txt $(COMPOSE_DIR)/.env"
	@echo "       nano $(COMPOSE_DIR)/.env"
	@echo ""
	@echo "  2. Edit the hw_proxy environment:"
	@echo "       cp $(REPO_DIR)/hw_proxy/hw_proxy/en.example.txt \\"
	@echo "          /opt/hw_proxy/hw_proxy/.env"
	@echo "       nano /opt/hw_proxy/hw_proxy/.env"
	@echo ""
	@echo "  3. (Optional) Generate Docker mTLS certs:"
	@echo "       make certs-docker"
	@echo ""
	@echo "  4. Import the CA into your browser/OS:"
	@echo "       $(COMPOSE_DIR)/traefik/certs/ca.pem"
	@echo ""
	@echo "  5. Start the stack:"
	@echo "       make up"
	@echo "================================================================"

# ──────────────────────────────────────────────────────────────────────────────
# System user
# ──────────────────────────────────────────────────────────────────────────────
install-user:
	@echo "[install-user] Ensuring $(HW_USER) exists..."
	@id -u $(HW_USER) >/dev/null 2>&1 \
	  && echo "[install-user] $(HW_USER) already exists — skipping creation." \
	  || sudo adduser --disabled-password --gecos "" $(HW_USER)
	@echo "[install-user] Adding $(HW_USER) to dialout and lp..."
	@sudo usermod -aG dialout,lp $(HW_USER)
	@echo "[install-user] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Sudoers — grant hw_user only reboot and shutdown
# ──────────────────────────────────────────────────────────────────────────────
install-sudoers:
	@echo "[install-sudoers] Writing /etc/sudoers.d/$(HW_USER)..."
	@printf \
	  'Defaults:$(HW_USER) !requiretty\n\n$(HW_USER) ALL=(root) NOPASSWD: \\\n    /opt/hw_proxy/hw_proxy/scripts/reboot.sh, \\\n    /opt/hw_proxy/hw_proxy/scripts/shutdown.sh\n' \
	  | sudo tee /etc/sudoers.d/$(HW_USER) > /dev/null
	@sudo chown root:root /etc/sudoers.d/$(HW_USER)
	@sudo chmod 440 /etc/sudoers.d/$(HW_USER)
	@sudo visudo -c -f /etc/sudoers.d/$(HW_USER)
	@echo "[install-sudoers] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Firewall — restrict hw_proxy and Traefik ports to the LAN subnet
# ──────────────────────────────────────────────────────────────────────────────
install-firewall:
	@echo "[install-firewall] Configuring ufw rules..."
	@sudo ufw allow from 192.168.1.0/24 to any port 9000 comment 'Odoo LAN'
	@sudo ufw allow from 192.168.1.0/24 to any port 9001 comment 'hw_status LAN'
	@sudo ufw allow from 172.16.0.0/12 to 10.254.254.1 port 9002 comment 'hw_proxy Docker mgmt only'
	@sudo ufw --force enable
	@sudo ufw status verbose
	@echo "[install-firewall] Done."

# ──────────────────────────────────────────────────────────────────────────────
# TLS certificates for Traefik
# ──────────────────────────────────────────────────────────────────────────────
certs-traefik:
	@echo "[certs-traefik] Generating Traefik TLS certificates..."
	@cd $(REPO_DIR)/docker-compose && \
	  bash scripts/generate_traefick_certs.sh $(DOMAIN) $(HOST_IP) $(CERT_NAME)
	@echo "[certs-traefik] Done. Import $(COMPOSE_DIR)/traefik/certs/ca.pem into your browser/OS."

# mTLS certificates for Docker daemon (optional, only if using Docker mTLS)
certs-docker:
	@echo "[certs-docker] Generating Docker mTLS certificates..."
	@DOCKER_HOST_IP=$(HOST_IP) sudo -E bash $(DOCKER_SCRIPTS)/manage_docker_certs.sh generate
	@echo "[certs-docker] Done. Restart Docker: sudo systemctl restart docker"

# ──────────────────────────────────────────────────────────────────────────────
# Deploy hw_proxy (venv + code sync)
# ──────────────────────────────────────────────────────────────────────────────
deploy-hw-proxy:
	@echo "[deploy-hw-proxy] Deploying hw_proxy (HW_USER=$(HW_USER))..."
	@sudo HW_USER=$(HW_USER) bash $(REPO_DIR)/hw_proxy/hw_proxy/scripts/update_hw_proxy.sh
	@echo "[deploy-hw-proxy] Done."

# Run the addon update script and restart the Odoo container.
# Use this after deploying changes to odoo_addons without rebuilding the stack.
update-odoo-addon:
	@echo "[update-odoo-addon] Running addon update script..."
	@sudo $(COMPOSE_DIR)/update_addon.sh
	@echo "[update-odoo-addon] Restarting Odoo container..."
	@sudo docker restart odoo_prod-fiesta_odoo-1
	@echo "[update-odoo-addon] Done."

# Pull latest code, redeploy hw_proxy venv, restart the systemd service.
# Use this for routine hw_proxy updates without touching the Docker stack.
update-hw-proxy:
	@echo "[update-hw-proxy] Pulling latest code from origin main..."
	@git -C $(REPO_DIR) pull origin main
	@echo "[update-hw-proxy] Running update script..."
	@$(SUDO) $(REPO_DIR)/hw_proxy/hw_proxy/scripts/update_hw_proxy.sh
	@echo "[update-hw-proxy] Restarting hw_proxy service..."
	@$(SUDO) systemctl restart hw_proxy
	@echo "[update-hw-proxy] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Systemd services
# ──────────────────────────────────────────────────────────────────────────────
install-systemd:
	@echo "[install-systemd] Installing systemd unit files..."
	@sudo cp $(SERVICES_DIR)/hw_proxy.service      /etc/systemd/system/hw_proxy.service
	@sudo cp $(SERVICES_DIR)/serial-config.service /etc/systemd/system/serial-config.service
	@sudo cp $(SERVICES_DIR)/odoo-pos.service      /etc/systemd/system/odoo-pos.service
	@sudo systemctl daemon-reload
	@sudo systemctl enable --now hw_proxy.service
	@sudo systemctl enable --now serial-config.service
	@sudo systemctl enable odoo-pos.service
	@echo "[install-systemd] Note: odoo-pos.service enabled but not started — run 'make up' first."
	@echo "[install-systemd] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Shared Docker networks (idempotent — safe to re-run)
# ──────────────────────────────────────────────────────────────────────────────
create-networks:
	@echo "[create-networks] Ensuring shared networks exist…"
	@$(SUDO) docker network inspect monitoring_shared >/dev/null 2>&1 \
	  || $(SUDO) docker network create monitoring_shared
	@echo "[create-networks] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Docker volume ownership for userns-remap
# ──────────────────────────────────────────────────────────────────────────────
volumes:
	@echo "[volumes] Fixing Docker volume ownership (userns-remap)..."
	@cd $(COMPOSE_DIR) && sudo bash $(SCRIPTS_DIR)/auto_chown_volumes.sh prod
	@echo "[volumes] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Docker image build
# ──────────────────────────────────────────────────────────────────────────────
build:
	@echo "[build] Building Docker images..."
	@cd $(COMPOSE_DIR) && sudo docker compose build
	@echo "[build] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Stack lifecycle
# ──────────────────────────────────────────────────────────────────────────────

# Rebuild images and (re)start odoo_prod + monitoring.
# Online (default):  make stack-up
# Offline/air-gap:   make stack-up OFFLINE=1
stack-up: create-networks
ifeq ($(OFFLINE),1)
	@echo "[stack-up] Offline mode: vendoring wheels and loading images…"
	@$(MAKE) -C $(REPO_DIR)/docker_offline load SUDO=$(SUDO)
endif
	@echo "[stack-up] Building Docker images…"
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose build
	@echo "[stack-up] Generating odoo.conf…"
	@cd $(COMPOSE_DIR) && $(SUDO) bash $(SCRIPTS_DIR)/generate_odoo_conf.sh
	@echo "[stack-up] Fixing volume ownership…"
	@cd $(COMPOSE_DIR) && $(SUDO) bash $(SCRIPTS_DIR)/auto_chown_volumes.sh prod
	@echo "[stack-up] Starting odoo_prod…"
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[stack-up] Starting monitoring…"
	@cd $(MONITORING_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[stack-up] Done. Use 'make logs' or 'make monitoring-logs' to follow output."

up: create-networks
	@echo "[up] Generating odoo.conf from .env..."
	@cd $(COMPOSE_DIR) && $(SUDO) bash $(SCRIPTS_DIR)/generate_odoo_conf.sh
	@echo "[up] Setting volume ownership..."
	@cd $(COMPOSE_DIR) && $(SUDO) bash $(SCRIPTS_DIR)/auto_chown_volumes.sh prod
	@echo "[up] Starting odoo_prod…"
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[up] Starting monitoring…"
	@cd $(MONITORING_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[up] All stacks running."

down:
	@echo "[down] Stopping odoo_prod stack..."
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose down
	@echo "[down] Done."

restart: down up

# ──────────────────────────────────────────────────────────────────────────────
# Monitoring stack
# ──────────────────────────────────────────────────────────────────────────────
monitoring-up: create-networks
	@echo "[monitoring-up] Starting monitoring stack…"
	@cd $(MONITORING_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[monitoring-up] Done."

monitoring-down:
	@echo "[monitoring-down] Stopping monitoring stack…"
	@cd $(MONITORING_DIR) && $(SUDO) docker compose down
	@echo "[monitoring-down] Done."

monitoring-logs:
	@cd $(MONITORING_DIR) && $(SUDO) docker compose logs -f --tail=100

# Reload Prometheus config live (SIGHUP — no restart, no data gap).
# Use after editing docker-compose/monitoring/prometheus.yml.
monitoring-reload-prometheus:
	@echo "[monitoring-reload-prometheus] Sending SIGHUP to Prometheus..."
	@cd $(MONITORING_DIR) && $(SUDO) docker compose kill -s SIGHUP prometheus
	@echo "[monitoring-reload-prometheus] Done. Verify: make monitoring-logs"

# Restart Grafana to apply provisioning changes (dashboards, datasources, alerts).
# Use after editing monitoring/grafana/provisioning/ or monitoring/grafana/dashboards/.
monitoring-reload-grafana:
	@echo "[monitoring-reload-grafana] Restarting Grafana..."
	@cd $(MONITORING_DIR) && $(SUDO) docker compose restart grafana
	@echo "[monitoring-reload-grafana] Done."

# Reload both: Prometheus config + Grafana provisioning.
monitoring-reload: monitoring-reload-prometheus monitoring-reload-grafana

# ──────────────────────────────────────────────────────────────────────────────
# Update — pull latest code and redeploy everything
# ──────────────────────────────────────────────────────────────────────────────
update:
	@$(MAKE) update-hw-proxy
	@echo "[update] Rebuilding Docker images..."
	@$(MAKE) build
	@echo "[update] Restarting Docker stack..."
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[update] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Observability
# ──────────────────────────────────────────────────────────────────────────────
logs:
	@cd $(COMPOSE_DIR) && sudo docker compose logs -f --tail=100

status:
	@echo "=== hw_proxy ==="
	@$(SUDO) systemctl status hw_proxy.service      --no-pager || true
	@echo ""
	@echo "=== serial-config ==="
	@$(SUDO) systemctl status serial-config.service --no-pager || true
	@echo ""
	@echo "=== odoo-pos ==="
	@$(SUDO) systemctl status odoo-pos.service      --no-pager || true
	@echo ""
	@echo "=== odoo_prod containers ==="
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose ps
	@echo ""
	@echo "=== monitoring containers ==="
	@cd $(MONITORING_DIR) && $(SUDO) docker compose ps

# ──────────────────────────────────────────────────────────────────────────────
# Database backup (pg_dump via hw_proxy script)
# ──────────────────────────────────────────────────────────────────────────────
backup:
	@echo "[backup] Triggering PostgreSQL database backup..."
	@sudo -u $(HW_USER) bash /opt/hw_proxy/hw_proxy/scripts/backup_odoo_db.sh
	@echo "[backup] Done."

# ──────────────────────────────────────────────────────────────────────────────
# Volume snapshot — disaster recovery backup / restore
#
# Backs up: postgres/pgdata + odoo/data (filestore).
# Rotation: keeps last 5 snapshots in BACKUP_DIR (default: /opt/backups/odoo_rafa).
# Expected size: ~120 MB compressed per snapshot.
# ──────────────────────────────────────────────────────────────────────────────
backup-volumes:
	@echo "[backup-volumes] Snapshotting critical volumes to $(BACKUP_DIR)..."
	@$(SUDO) bash $(SCRIPTS_DIR)/backup_volumes.sh "$(COMPOSE_DIR)" "$(BACKUP_DIR)"
	@echo "[backup-volumes] Done."

# Usage: make restore-volumes BACKUP=/opt/backups/odoo_rafa/2026-05-30_14-00-00
restore-volumes:
	@test -n "$(BACKUP)" \
	  || { echo "ERROR: BACKUP variable required.  Usage: make restore-volumes BACKUP=<path>"; exit 1; }
	@echo "[restore-volumes] Stopping stacks..."
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose stop || true
	@cd $(MONITORING_DIR) && $(SUDO) docker compose stop || true
	@echo "[restore-volumes] Restoring volumes from $(BACKUP)..."
	@$(SUDO) bash $(SCRIPTS_DIR)/restore_volumes.sh "$(COMPOSE_DIR)" "$(BACKUP)"
	@echo "[restore-volumes] Restarting stacks..."
	@cd $(COMPOSE_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@cd $(MONITORING_DIR) && $(SUDO) docker compose up -d --remove-orphans
	@echo "[restore-volumes] Done. Verify Odoo loads correctly."
