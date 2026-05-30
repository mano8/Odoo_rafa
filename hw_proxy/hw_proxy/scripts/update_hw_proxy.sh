#!/usr/bin/env bash
# ==============================================================================
# update_hw_proxy.sh
#
#  Must be run as root (e.g. via `sudo update_hw_proxy.sh`).
#  Steps:
#    1) Ensure /opt/hw_proxy exists (owned by HW_USER, mode 755).
#    2) Create a Python venv under /opt/hw_proxy/.venv.
#    3) rsync the hw_proxy source into /opt/hw_proxy/hw_proxy.
#    4) Install Python requirements — wheelhouse if present, else PyPI.
#    5) Lock down ownership/permissions of .venv and application code.
#    6) Ensure scripts/ are owned by HW_USER with mode 750.
#
#  Usage:
#    sudo /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/update_hw_proxy.sh
#
# ==============================================================================
set -euo pipefail
shopt -s inherit_errexit 2>/dev/null || true
umask 022

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
REPO_DIR="/opt/Odoo_rafa"
SRC_BASE="$REPO_DIR/hw_proxy"
APP_SRC_DIR="$SRC_BASE/hw_proxy"
REQUIREMENTS_FILE="$APP_SRC_DIR/requirements.txt"
WHEELHOUSE_DIR="$SRC_BASE/wheelhouse"

DST_BASE="/opt/hw_proxy"
APP_DST_DIR="$DST_BASE/hw_proxy"
VENV_DIR="$DST_BASE/.venv"

ADMIN_USER="${HW_USER:-hw_user}"
SCRIPTS_DIR="$APP_DST_DIR/scripts"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
fail() { echo >&2 "ERROR: $*"; exit 1; }
info() { echo ">> $*"; }

# ------------------------------------------------------------------------------
# Must run as root
# ------------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] || fail "This script must be run as root. Try 'sudo $0'."

# ------------------------------------------------------------------------------
# Verify source
# ------------------------------------------------------------------------------
[ -d "$APP_SRC_DIR" ]    || fail "Source directory '$APP_SRC_DIR' does not exist."
[ -f "$REQUIREMENTS_FILE" ] || fail "Requirements file '$REQUIREMENTS_FILE' not found."

# ------------------------------------------------------------------------------
# Step 1 — Ensure /opt/hw_proxy exists
# ------------------------------------------------------------------------------
info "Step 1: Ensuring '$DST_BASE' exists (owner=$ADMIN_USER)…"
mkdir -p "$DST_BASE"
chown -R "$ADMIN_USER":"$ADMIN_USER" "$DST_BASE"
chmod 755 "$DST_BASE"

# ------------------------------------------------------------------------------
# Step 2 — Create Python venv
# ------------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    info "Step 2: Creating virtualenv at '$VENV_DIR'…"
    runuser -u "$ADMIN_USER" -- python3 -m venv "$VENV_DIR"
else
    info "Step 2: Virtualenv already exists — skipping creation."
fi
chown -R "$ADMIN_USER":"$ADMIN_USER" "$VENV_DIR"
find "$VENV_DIR" -type d -exec chmod 755 {} \;
find "$VENV_DIR" -type f -exec chmod 644 {} \;
find "$VENV_DIR/bin" -type f -exec chmod 755 {} \;

# ------------------------------------------------------------------------------
# Step 3 — Rsync source
# ------------------------------------------------------------------------------
info "Step 3: Syncing source '$APP_SRC_DIR' → '$APP_DST_DIR'…"
mkdir -p "$APP_DST_DIR"
chown "$ADMIN_USER":"$ADMIN_USER" "$APP_DST_DIR"
runuser -u "$ADMIN_USER" -- rsync -a --delete \
    --exclude="__pycache__" \
    --exclude=".venv" \
    "$APP_SRC_DIR"/ "$APP_DST_DIR"/

# ------------------------------------------------------------------------------
# Step 4 — Install Python requirements (wheelhouse first, then PyPI)
# ------------------------------------------------------------------------------
if [ -d "$WHEELHOUSE_DIR" ] && [ -n "$(ls -A "$WHEELHOUSE_DIR" 2>/dev/null)" ]; then
    info "Step 4: Wheelhouse found at '$WHEELHOUSE_DIR' — installing offline…"
    runuser -u "$ADMIN_USER" -- "$VENV_DIR/bin/python" -m pip install \
        --no-index \
        --find-links="$WHEELHOUSE_DIR" \
        -r "$REQUIREMENTS_FILE"
else
    info "Step 4: No wheelhouse found — checking PyPI connectivity…"
    if ! curl -sSf --connect-timeout 5 https://pypi.org/ >/dev/null 2>&1; then
        fail "No wheelhouse and PyPI unreachable. Run 'make -C $REPO_DIR/docker_offline wheels' first."
    fi
    info "        PyPI reachable — installing from PyPI…"
    runuser -u "$ADMIN_USER" -- "$VENV_DIR/bin/python" -m pip install \
        --upgrade -r "$REQUIREMENTS_FILE"
fi

# ------------------------------------------------------------------------------
# Step 5 — Secure application code
# ------------------------------------------------------------------------------
info "Step 5: Locking down ownership and permissions…"
chown -R "$ADMIN_USER":"$ADMIN_USER" "$APP_DST_DIR"
find "$APP_DST_DIR" -type d -exec chmod 755 {} \;
find "$APP_DST_DIR" -type f -exec chmod 644 {} \;

# ------------------------------------------------------------------------------
# Step 6 — Harden scripts/
# ------------------------------------------------------------------------------
if [ -d "$SCRIPTS_DIR" ]; then
    info "Step 6: Hardening '$SCRIPTS_DIR' (mode=750)…"
    chown -R "$ADMIN_USER":"$ADMIN_USER" "$SCRIPTS_DIR"
    find "$SCRIPTS_DIR" -type f -name "*.sh" -exec chmod 750 {} \;
else
    info "Step 6: No scripts/ directory found — skipping."
fi

info "Deployment completed successfully."
exit 0
