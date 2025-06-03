#!/usr/bin/env bash
# ==============================================================================
# deploy.sh
#
#  This script must be run as root (e.g. via `sudo deploy.sh`).
#  It will:
#    1) Ensure /opt/hw_proxy exists (owned by zepos, mode 755).
#    2) Create a Python venv under /opt/hw_proxy/.venv (as user "zepos").
#    3) rsync the hw_proxy source into /opt/hw_proxy/hw_proxy (as "zepos").
#    4) Verify Internet → PyPI is reachable.
#    5) Install/upgrade Python requirements inside that venv (as "zepos").
#    6) Lock down ownership/permissions of .venv and application code.
#    7) Ensure any “scripts/” folder is owned by zepos and scripts are 750.
#
#  Failure in any step will abort immediately (due to `set -euo pipefail`).
#
#  Usage:
#    sudo /opt/Odoo_rafa/hw_proxy/deploy.sh
#
# ------------------------------------------------------------------------------
set -euo pipefail
shopt -s inherit_errexit 2>/dev/null || true
umask 022

# ------------------------------------------------------------------------------
# 1) Configuration variables
# ------------------------------------------------------------------------------
REPO_DIR="/opt/Odoo_rafa"
SRC_BASE="$REPO_DIR/hw_proxy"
APP_SRC_DIR="$SRC_BASE/hw_proxy"
REQUIREMENTS_FILE="$APP_SRC_DIR/requirements.txt"

DST_BASE="/opt/hw_proxy"
APP_DST_DIR="$DST_BASE/hw_proxy"
VENV_DIR="$DST_BASE/.venv"

ADMIN_USER="zepos"
SCRIPT_SUBDIR="scripts"
SCRIPTS_DIR="$APP_DST_DIR/$SCRIPT_SUBDIR"

# ------------------------------------------------------------------------------
# 2) Helpers
# ------------------------------------------------------------------------------
fail () {
    echo >&2 "ERROR: $*"
    exit 1
}

info () {
    echo ">> $*"
}

# ------------------------------------------------------------------------------
# 3) Must be run as root
# ------------------------------------------------------------------------------
if [ "$(id -u)" -ne 0 ]; then
    fail "This script must be run as root. Try 'sudo $0'."
fi

# ------------------------------------------------------------------------------
# 4) Verify source directory and requirements.txt
# ------------------------------------------------------------------------------
[ -d "$APP_SRC_DIR" ] \
    || fail "Source directory '$APP_SRC_DIR' does not exist."

[ -f "$REQUIREMENTS_FILE" ] \
    || fail "Requirements file '$REQUIREMENTS_FILE' not found."

# ------------------------------------------------------------------------------
# 5) Step 1 – Ensure /opt/hw_proxy exists (owner=zepos, mode=755)
# ------------------------------------------------------------------------------
info "Step 1: Ensuring '$DST_BASE' exists and is owned by $ADMIN_USER…"
if [ ! -d "$DST_BASE" ]; then
    mkdir -p "$DST_BASE"
fi
chown -R "$ADMIN_USER":"$ADMIN_USER" "$DST_BASE"
chmod 755 "$DST_BASE"

# ------------------------------------------------------------------------------
# 6) Step 2 – Create Python venv under /opt/hw_proxy/.venv (as zepos)
# ------------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    info "Step 2: Creating Python virtualenv at '$VENV_DIR' (as $ADMIN_USER)…"
    runuser -u "$ADMIN_USER" -- python3 -m venv "$VENV_DIR"
else
    info "Step 2: Virtualenv already exists at '$VENV_DIR'; skipping creation."
fi

info "       Securing venv permissions…"
chown -R "$ADMIN_USER":"$ADMIN_USER" "$VENV_DIR"
find "$VENV_DIR" -type d -exec chmod 755 {} \;
find "$VENV_DIR" -type f -exec chmod 644 {} \;
find "$VENV_DIR/bin" -type f -exec chmod 755 {} \;

# ------------------------------------------------------------------------------
# 7) Step 3 – Rsync source → /opt/hw_proxy/hw_proxy (as zepos)
# ------------------------------------------------------------------------------
info "Step 3: Syncing application code from '$APP_SRC_DIR' → '$APP_DST_DIR' (as $ADMIN_USER)…"
mkdir -p "$APP_DST_DIR"
chown "$ADMIN_USER":"$ADMIN_USER" "$APP_DST_DIR"
runuser -u "$ADMIN_USER" -- rsync -a --delete \
    --exclude="__pycache__" \
    --exclude=".venv" \
    "$APP_SRC_DIR"/ "$APP_DST_DIR"/

# ------------------------------------------------------------------------------
# 8) Step 4 – Check Internet connectivity to PyPI before pip install
# ------------------------------------------------------------------------------
info "Step 4: Checking connectivity to PyPI.org…"
if ! curl -sSf --connect-timeout 5 https://pypi.org/ >/dev/null 2>&1; then
    fail "Unable to reach https://pypi.org. Verify network access before installing Python packages."
fi

# ------------------------------------------------------------------------------
# 9) Step 5 – Install/upgrade requirements inside venv (as zepos)
# ------------------------------------------------------------------------------
info "Step 5: Installing/upgrading Python packages from '$REQUIREMENTS_FILE'…"
runuser -u "$ADMIN_USER" -- "$VENV_DIR/bin/python" -m pip install --upgrade -r "$REQUIREMENTS_FILE"

# ------------------------------------------------------------------------------
# 10) Step 6 – Secure application code ownership/permissions
# ------------------------------------------------------------------------------
info "Step 6: Locking down ownership and permissions of application code…"
chown -R "$ADMIN_USER":"$ADMIN_USER" "$APP_DST_DIR"
find "$APP_DST_DIR" -type d -exec chmod 755 {} \;
find "$APP_DST_DIR" -type f -exec chmod 644 {} \;

# ------------------------------------------------------------------------------
# 11) Step 7 – Ensure scripts/ are owned by zepos with mode 750
# ------------------------------------------------------------------------------
if [ -d "$SCRIPTS_DIR" ]; then
    info "Step 7: Hardening '$SCRIPTS_DIR' (owner=$ADMIN_USER, mode=750)…"
    chown -R "$ADMIN_USER":"$ADMIN_USER" "$SCRIPTS_DIR"
    find "$SCRIPTS_DIR" -type f -name "*.sh" -exec chmod 750 {} \;
else
    info "Step 7: No '$SCRIPTS_DIR' directory found; skipping."
fi

# ------------------------------------------------------------------------------
# 12) Done
# ------------------------------------------------------------------------------
info "Deployment completed successfully."
exit 0