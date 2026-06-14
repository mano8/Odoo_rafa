"""Transport-agnostic ESC/POS printer state machine.

Models the one characteristic that matters for the receipt-drop bug: a finite
**input buffer** that is filled by the host (USB/serial/TCP) far faster than the
print head can empty it.  Bytes arrive instantly; the head drains the buffer at
``drain_rate_bps``.  When the host pushes a batch of receipts with no pacing the
buffer fills and overflows — exactly the PP6800 "6 ok, 7 breaks" cliff.  Pacing
the writes (or chunking them, or waiting on the in-band status) keeps buffer
occupancy bounded and prevents the overflow.

The model is driven by a clock (``clock`` callable, default ``time.monotonic``)
so tests can advance time deterministically instead of sleeping.

In-band ESC/POS real-time replies are answered so the emulator works as a real
``escpos`` device over both transports:

* ``DLE EOT n`` (``10 04 n``) — real-time status request → one status byte.
* ``DLE ENQ 2`` (``10 05 02``) — clear the input and print buffers.
* ``ESC @``     (``1B 40``)    — initialise; resets modes but, per the ESC/POS
  spec, does **not** clear the receive buffer.
* ``GS V``      (``1D 56``)    — cut; delimits one job (used by ``max_queued_jobs``).
"""

from __future__ import annotations

import time
from typing import Callable, Literal

OverflowBehavior = Literal["drop", "truncate", "garble", "go_offline"]

# ── ESC/POS control bytes ────────────────────────────────────────────────────
_DLE = 0x10
_EOT = 0x04
_ENQ = 0x05
_ESC = 0x1B
_GS = 0x1D
_AT = 0x40  # ESC @ → init
_V = 0x56  # GS V  → cut

# Real-time status reply masks (match python-escpos escpos/constants.py):
#   is_online()    → not (byte & 8)
#   paper_status() → no_paper if byte & 96 == 96; near_end if byte & 12 == 12
_MASK_ONLINE = 0x08
_MASK_NOPAPER = 0x60
_MASK_LOWPAPER = 0x0C
# Healthy reply byte: online, paper ok (none of the fault bits set, fixed bits 1+4).
_STATUS_OK = 0x12


class PrinterEmulator:
    """A printer whose input buffer fills instantly and drains at a fixed rate.

    All sizes are in bytes; ``drain_rate_bps`` is the head print speed in
    bytes/second (e.g. ``11_520`` ≈ 115 200 baud / 10 bits per byte).
    """

    def __init__(
        self,
        *,
        buffer_size: int,
        drain_rate_bps: float,
        max_queued_jobs: int | None = None,
        overflow_behavior: OverflowBehavior = "drop",
        paper_status: Literal["ok", "near_end", "no_paper"] = "ok",
        online: bool = True,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.buffer_size = buffer_size
        self.drain_rate_bps = drain_rate_bps
        self.max_queued_jobs = max_queued_jobs
        self.overflow_behavior = overflow_behavior
        self.paper_status = paper_status
        self.online = online
        self._clock = clock

        self._buffered = 0  # bytes currently waiting in the input buffer
        self._last_drain = clock()
        # Cumulative counters (monotonic for the printer's lifetime).
        self.bytes_received = 0  # everything the host sent (incl. dropped)
        self.bytes_accepted = 0  # bytes that made it into the buffer
        self.bytes_printed = 0  # bytes drained by the head
        self.overflow_events = 0
        self.overflow_bytes = 0
        # Cut offsets in *accepted* byte terms; a job has printed once the head
        # has drained past its cut.
        self._cut_offsets: list[int] = []

    # ------------------------------------------------------------------ #
    # Observable state                                                     #
    # ------------------------------------------------------------------ #

    @property
    def pending_bytes(self) -> int:
        """Bytes still in the buffer waiting to print (drained to *now*)."""
        self._advance()
        return self._buffered

    @property
    def jobs_printed(self) -> int:
        """Number of cut-delimited jobs the head has fully printed."""
        self._advance()
        return sum(1 for off in self._cut_offsets if off <= self.bytes_printed)

    @property
    def jobs_queued(self) -> int:
        """Cut-delimited jobs received but not yet fully printed."""
        return len(self._cut_offsets) - self.jobs_printed

    def status(self) -> dict:
        """Snapshot of the emulator's counters (for the status endpoint/log)."""
        return {
            "online": self.online,
            "paper_status": self.paper_status,
            "buffer_size": self.buffer_size,
            "pending_bytes": self.pending_bytes,
            "bytes_received": self.bytes_received,
            "bytes_accepted": self.bytes_accepted,
            "bytes_printed": self.bytes_printed,
            "jobs_printed": self.jobs_printed,
            "jobs_queued": self.jobs_queued,
            "overflow_events": self.overflow_events,
            "overflow_bytes": self.overflow_bytes,
        }

    # ------------------------------------------------------------------ #
    # Time / draining                                                      #
    # ------------------------------------------------------------------ #

    def _advance(self) -> None:
        """Drain the buffer for the wall-clock time elapsed since last call."""
        now = self._clock()
        elapsed = now - self._last_drain
        self._last_drain = now
        if elapsed <= 0 or not self.online:
            return
        printable = int(elapsed * self.drain_rate_bps)
        consumed = min(self._buffered, printable)
        self._buffered -= consumed
        self.bytes_printed += consumed

    # ------------------------------------------------------------------ #
    # Host input                                                           #
    # ------------------------------------------------------------------ #

    def feed(self, data: bytes) -> bytes:
        """Process bytes from the host; return any in-band reply bytes.

        Real-time commands are answered immediately (even when the buffer is
        full); everything else is accounted against the input buffer, applying
        ``overflow_behavior`` once the buffer is exceeded.
        """
        self._advance()
        self.bytes_received += len(data)
        reply = bytearray()
        payload, replies = self._extract_realtime(data)
        reply.extend(replies)
        self._accept(payload)
        return bytes(reply)

    def _extract_realtime(self, data: bytes) -> tuple[bytes, bytes]:
        """Split real-time commands out of ``data``; return (payload, replies).

        ``payload`` is the byte stream destined for the buffer (print data plus
        non-real-time commands); ``replies`` is what the printer sends back.
        """
        payload = bytearray()
        reply = bytearray()
        i = 0
        n = len(data)
        while i < n:
            b = data[i]
            if b == _DLE and i + 2 < n and data[i + 1] == _EOT:
                reply.append(self._status_byte())
                i += 3
                continue
            if b == _DLE and i + 2 < n and data[i + 1] == _ENQ:
                if data[i + 2] == 0x02:
                    self._clear_buffers()
                i += 3
                continue
            payload.append(b)
            i += 1
        return bytes(payload), bytes(reply)

    def _accept(self, payload: bytes) -> None:
        """Account ``payload`` bytes against the buffer, honouring overflow."""
        if not payload:
            return
        free = self.buffer_size - self._buffered
        # A full buffer (or one job too many) overflows per the configured mode.
        too_many_jobs = (
            self.max_queued_jobs is not None
            and self.jobs_queued >= self.max_queued_jobs
        )
        overflow = len(payload) - free
        if overflow > 0 or too_many_jobs:
            self._handle_overflow(max(overflow, 0))
        accepted = payload if overflow <= 0 else payload[:free]
        self._buffered += len(accepted)
        self.bytes_accepted += len(accepted)
        self._record_cuts(accepted)

    def _handle_overflow(self, dropped: int) -> None:
        self.overflow_events += 1
        self.overflow_bytes += dropped
        if self.overflow_behavior == "go_offline":
            self.online = False

    def _record_cuts(self, accepted: bytes) -> None:
        """Record the accepted-byte offset of every GS V cut in ``accepted``."""
        base = self.bytes_accepted - len(accepted)
        i = 0
        while i < len(accepted) - 1:
            if accepted[i] == _GS and accepted[i + 1] == _V:
                self._cut_offsets.append(base + i + 2)
                i += 2
                continue
            i += 1

    # ------------------------------------------------------------------ #
    # Real-time handlers                                                   #
    # ------------------------------------------------------------------ #

    def _status_byte(self) -> int:
        byte = _STATUS_OK
        if not self.online:
            byte |= _MASK_ONLINE
        if self.paper_status == "no_paper":
            byte |= _MASK_NOPAPER
        elif self.paper_status == "near_end":
            byte |= _MASK_LOWPAPER
        return byte

    def _clear_buffers(self) -> None:
        """DLE ENQ 2 — drop everything pending; bring the printer back online."""
        self._buffered = 0
        self._cut_offsets = [off for off in self._cut_offsets if off <= self.bytes_printed]
        self.online = True
