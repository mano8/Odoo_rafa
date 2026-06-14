"""asyncio TCP transport for :class:`PrinterEmulator`.

Used by the Docker stack: hw_proxy talks to the emulator as an escpos
``Network`` device (default port 9100), which works cleanly across containers
with no shared PTY.  All connections share one emulator instance — there is only
one physical printer.
"""

from __future__ import annotations

import asyncio
import logging

from emulator.core import PrinterEmulator

logger = logging.getLogger("emulated_printer")


class TcpPrinterServer:
    """Serve one :class:`PrinterEmulator` over a TCP socket."""

    def __init__(self, emulator: PrinterEmulator, host: str, port: int) -> None:
        self._emulator = emulator
        self._host = host
        self._port = port

    async def serve_forever(self) -> None:
        server = await asyncio.start_server(
            self._handle_client, self._host, self._port
        )
        addr = ", ".join(str(s.getsockname()) for s in server.sockets)
        logger.info("[emulated_printer] TCP listening on %s", addr)
        async with server:
            await server.serve_forever()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername")
        logger.info("[emulated_printer] client connected: %s", peer)
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                reply = self._emulator.feed(data)
                if reply:
                    writer.write(reply)
                    await writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            writer.close()
            logger.info(
                "[emulated_printer] client closed: %s  status=%s",
                peer,
                self._emulator.status(),
            )
