"""Prometheus metrics endpoint for the printer emulator.

Exposes the emulator's **ground-truth** counters (true buffer overflow, bytes
dropped, jobs printed/queued, buffer occupancy) so the dev_emulated Grafana
stack can chart what the real PP6800 cannot report.  A custom collector reads
:meth:`PrinterEmulator.status` lazily on every scrape, so the values are always
current (the head drains on read).

The names mirror the metrics requested for the dashboard: ``overflow_events``,
``overflow_bytes``, ``jobs_printed``, ``jobs_queued``, ``buffer_size``.  They are
exposed as gauges (exact names, no ``_total`` suffix); the cumulative ones are
monotonic, so ``increase()``/``rate()`` in Grafana give per-session deltas.
"""

from __future__ import annotations

import logging

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

from emulator.core import PrinterEmulator

logger = logging.getLogger("emulated_printer")

_PREFIX = "emulated_printer"


class _EmulatorCollector:
    """Yield the live emulator counters as Prometheus gauges on each scrape."""

    def __init__(self, emulator: PrinterEmulator) -> None:
        self._emulator = emulator

    def collect(self):
        s = self._emulator.status()
        metrics = {
            "online": (s["online"] and 1 or 0, "Printer online: 1=online, 0=offline."),
            "buffer_size_bytes": (s["buffer_size"], "Configured input-buffer size in bytes."),
            "pending_bytes": (s["pending_bytes"], "Bytes still waiting in the buffer."),
            "jobs_printed": (s["jobs_printed"], "Cut-delimited jobs fully printed (cumulative)."),
            "jobs_queued": (s["jobs_queued"], "Jobs received but not yet printed."),
            "overflow_events": (s["overflow_events"], "Buffer-overflow events (cumulative)."),
            "overflow_bytes": (s["overflow_bytes"], "Bytes dropped on overflow (cumulative)."),
            "bytes_received": (s["bytes_received"], "Bytes received from the host (cumulative)."),
            "bytes_printed": (s["bytes_printed"], "Bytes printed by the head (cumulative)."),
        }
        for name, (value, doc) in metrics.items():
            yield GaugeMetricFamily(f"{_PREFIX}_{name}", doc, value=value)


def start_metrics_server(emulator: PrinterEmulator, port: int) -> None:
    """Register the collector and serve Prometheus metrics on ``port``."""
    REGISTRY.register(_EmulatorCollector(emulator))
    start_http_server(port)
    logger.info("[emulated_printer] metrics listening on :%d", port)
