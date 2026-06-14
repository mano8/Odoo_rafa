"""Runtime-tunable printer settings (shared dataclass + wire model).

Defined here in ``schemas`` so it can be used both as the live settings object
on :class:`~hw_proxy.core.printer_pool.PrinterPool` and as the request/response
body for the ``/system/print_settings`` endpoints, without ``core`` and
``schemas`` importing each other (one-way dependency: ``schemas`` ← ``core``).
"""

from typing import Literal

from pydantic import BaseModel, Field

PrintStrategy = Literal["pace", "chunked", "status_poll"]


class PrintSettings(BaseModel):
    """Mutable print-pipeline settings, tunable at runtime from the hw_status UI.

    One of three flow-control strategies paces the drain worker so a batch of
    receipts cannot overflow the printer's small input buffer:

      ``pace``        — sleep an estimated print time after each job.
      ``chunked``     — write the payload in small slices with gaps between them.
      ``status_poll`` — wait until the printer reports ready before the next job.

    All durations are milliseconds so the UI can expose plain integer inputs.
    """

    strategy: PrintStrategy = "pace"

    # pace strategy
    pace_base_ms: int = Field(default=800, ge=0, le=10_000)
    pace_per_line_ms: int = Field(default=30, ge=0, le=2_000)

    # chunked strategy
    chunk_size: int = Field(default=256, ge=16, le=4_096)
    chunk_delay_ms: int = Field(default=20, ge=0, le=2_000)

    # status_poll strategy
    status_poll_timeout_ms: int = Field(default=5_000, ge=0, le=60_000)
    status_poll_interval_ms: int = Field(default=100, ge=10, le=5_000)
