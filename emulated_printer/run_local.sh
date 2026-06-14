#!/usr/bin/env bash
# Serial/PTY transport launcher — run INSIDE the Linux container.
#
# Windows has no socat, so this is not a host script: use it in the emulator
# container (it ships socat) or in the combined image (Dockerfile.serial).  It
# mirrors the vedirect virtual-serial-port recipe: socat makes a PTY pair, the
# emulator opens one end, and hw_proxy opens the other as a Serial device.
set -euo pipefail

PTY_PRINTER="${PTY_PRINTER:-/tmp/printer0}"   # emulator opens this end
PTY_PROXY="${PTY_PROXY:-/tmp/printer1}"       # hw_proxy opens this end (devfile)
CONFIG="${CONFIG:-config/pp6800.yml}"

echo "[run_local] socat PTY pair: ${PTY_PRINTER} <-> ${PTY_PROXY}"
socat -d -d "PTY,raw,echo=0,link=${PTY_PRINTER}" \
            "PTY,raw,echo=0,link=${PTY_PROXY}" &
SOCAT_PID=$!
trap 'kill "${SOCAT_PID}" 2>/dev/null || true' EXIT

# Wait for socat to create the links before opening them.
for _ in $(seq 1 50); do
  [ -e "${PTY_PRINTER}" ] && break
  sleep 0.1
done

echo "[run_local] starting emulator on ${PTY_PRINTER}"
exec python server.py --config "${CONFIG}" --transport pty --pty "${PTY_PRINTER}"
