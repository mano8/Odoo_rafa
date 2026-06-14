#!/usr/bin/env bash
# Combined serial-fidelity launcher for Dockerfile.serial.
#
# Runs socat + the emulator + hw_proxy in ONE container so they can share a PTY
# pair (PTYs cannot be bridged across containers — that is why the default stack
# uses TCP).  socat links one end to /dev/ttyACM0 so hw_proxy can open it with
# the unchanged PP6800 serial profile, giving full serial-transport fidelity.
set -euo pipefail

PTY_PRINTER="/tmp/printer0"          # emulator end
PTY_PROXY="/dev/ttyACM0"             # hw_proxy end (PP6800 devfile)
CONFIG="${CONFIG:-/opt/emulated_printer/config/pp6800.yml}"

echo "[start_serial] socat PTY pair: ${PTY_PRINTER} <-> ${PTY_PROXY}"
socat -d -d "PTY,raw,echo=0,link=${PTY_PRINTER}" \
            "PTY,raw,echo=0,link=${PTY_PROXY}" &
trap 'kill 0' EXIT

for _ in $(seq 1 50); do
  [ -e "${PTY_PRINTER}" ] && [ -e "${PTY_PROXY}" ] && break
  sleep 0.1
done
chmod a+rw "${PTY_PROXY}" 2>/dev/null || true

echo "[start_serial] starting emulator on ${PTY_PRINTER}"
(cd /opt/emulated_printer && \
  python server.py --config "${CONFIG}" --transport pty --pty "${PTY_PRINTER}") &

echo "[start_serial] starting hw_proxy (PRINTER_KEY=${PRINTER_KEY:-PP6800})"
exec uvicorn hw_proxy.main:app --host 0.0.0.0 --port 9002 \
  --proxy-headers --forwarded-allow-ips "*"
