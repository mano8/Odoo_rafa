"""socat/PTY transport for :class:`PrinterEmulator` (full serial fidelity).

Mirrors the vedirect approach: ``socat`` makes a PTY pair, the emulator opens
one end, hw_proxy opens the other as an escpos ``Serial`` device.  Windows has
no ``socat``, so this path only runs **inside the Linux container** (see
``run_local.sh`` / ``Dockerfile.serial``); for cross-container use prefer the TCP
transport.
"""

from __future__ import annotations

import asyncio
import logging

import serial

from emulator.core import PrinterEmulator

logger = logging.getLogger("emulated_printer")


class PtyPrinterServer:
    """Serve one :class:`PrinterEmulator` over a serial/PTY device."""

    def __init__(
        self, emulator: PrinterEmulator, devfile: str, baudrate: int = 115200
    ) -> None:
        self._emulator = emulator
        self._devfile = devfile
        self._baudrate = baudrate

    async def serve_forever(self) -> None:
        ser = serial.Serial(self._devfile, self._baudrate, timeout=0)
        logger.info(
            "[emulated_printer] serial listening on %s @ %d",
            self._devfile,
            self._baudrate,
        )
        try:
            while True:
                data = await asyncio.to_thread(self._read, ser)
                if data:
                    reply = self._emulator.feed(data)
                    if reply:
                        ser.write(reply)
                        ser.flush()
                else:
                    await asyncio.sleep(0.005)
        finally:
            ser.close()

    @staticmethod
    def _read(ser: "serial.Serial") -> bytes:
        waiting = ser.in_waiting
        return ser.read(waiting) if waiting else b""
