"""Entrypoint: load a printer profile and serve it over TCP or a PTY.

Examples
--------
TCP (Docker stack default)::

    python server.py --config config/pp6800.yml --transport tcp --host 0.0.0.0 --port 9100

Serial/PTY (inside the container, full fidelity)::

    socat -d -d PTY,raw,echo=0,link=/tmp/printer0 PTY,raw,echo=0,link=/tmp/printer1 &
    python server.py --config config/pp6800.yml --transport pty --pty /tmp/printer0
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from pathlib import Path

import yaml

from emulator.core import PrinterEmulator

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("emulated_printer")

_PROFILE_KEYS = (
    "buffer_size",
    "drain_rate_bps",
    "max_queued_jobs",
    "overflow_behavior",
    "paper_status",
    "online",
)


def load_profile(path: str) -> dict:
    """Read the YAML profile, keeping only the keys the emulator understands."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return {k: data[k] for k in _PROFILE_KEYS if k in data}


def build_emulator(profile: dict) -> PrinterEmulator:
    return PrinterEmulator(**profile)


async def _run(args: argparse.Namespace) -> None:
    emulator = build_emulator(load_profile(args.config))
    logger.info("[emulated_printer] profile=%s", emulator.status())
    if args.transport == "tcp":
        from emulator.tcp_server import TcpPrinterServer

        await TcpPrinterServer(emulator, args.host, args.port).serve_forever()
    else:
        from emulator.pty_server import PtyPrinterServer

        await PtyPrinterServer(emulator, args.pty, args.baudrate).serve_forever()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Controllable ESC/POS printer emulator")
    p.add_argument("--config", default=os.environ.get("PROFILE", "config/pp6800.yml"))
    p.add_argument(
        "--transport",
        choices=("tcp", "pty"),
        default=os.environ.get("TRANSPORT", "tcp"),
    )
    p.add_argument("--host", default=os.environ.get("BIND_HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.environ.get("BIND_PORT", "9100")))
    p.add_argument("--pty", default=os.environ.get("PTY_DEVICE", "/tmp/printer0"))
    p.add_argument(
        "--baudrate", type=int, default=int(os.environ.get("BAUDRATE", "115200"))
    )
    return p.parse_args()


if __name__ == "__main__":
    try:
        asyncio.run(_run(_parse_args()))
    except KeyboardInterrupt:
        pass
