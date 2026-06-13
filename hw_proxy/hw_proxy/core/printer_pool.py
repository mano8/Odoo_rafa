"""
Persistent printer connection pool with fire-and-forget serial writes.

Bottleneck analysis (usbipd-win + PP6800):
  55 918 bytes × 10 bits ÷ 115 200 baud = 4.86 s  ← hardware floor

The printer's USB-CDC/ACM interface has an internal UART that honours the
115 200 baud line-coding.  There is no software fix for the raw transfer
time.  The practical fix is to return success to Odoo as soon as the
ESC/POS payload is encoded (~25 ms) and let a background task drain the
serial port.

Concurrency model
─────────────────
• _encode_receipt   — runs in asyncio.to_thread (pure Pillow/ESC-POS, no I/O)
• _background_write — asyncio.Task; acquires _async_lock, then runs the
                      actual serial write in a thread.  Holds the lock until
                      the USB-CDC/ACM FIFO has fully drained to the printer
                      UART (~4.86 s for 56 KB at 115 200 baud) so that the
                      next job's _close() never interrupts an ongoing transfer.
• get_full_status   — if the lock is currently held (write in progress)
                      returns the cached status instantly; otherwise
                      acquires the lock and queries the printer.
"""

import asyncio
import logging
import time
import warnings
from typing import Optional, get_args

from escpos.printer import Dummy
from PIL import Image, ImageOps

from hw_proxy.core.exceptions import HwPrinterError
from hw_proxy.metrics import (
    print_duration_seconds,
    print_jobs_total,
    print_overflow_bytes_total,
    print_overflow_events_total,
    print_queue_depth,
    print_setting,
    print_strategy_active,
    printer_buffer_size_bytes,
    serial_write_duration_seconds,
)
from hw_proxy.schemas.printer import PrintSettings, PrintStrategy
from hw_proxy.schemas.receipt import PrintReceiptJsonRequest
from hw_proxy.tools.pos_helper import EscPosHelper

logger = logging.getLogger("hw_proxy")

# All flow-control strategies, for publishing the active one as a metric.
_PRINT_STRATEGIES = get_args(PrintStrategy)

# Width/height ESC/POS multipliers per size level (1-indexed; index 0 unused).
# Level 1 (Small):  1× wide, 1× tall  → 42 chars/line
# Level 2 (Normal): 1× wide, 2× tall  → 42 chars/line, double-height glyphs
# Level 3 (Big):    2× wide, 2× tall  → 21 chars/line
_SZ_W = (0, 1, 1, 2)
_SZ_H = (0, 1, 2, 2)

_CMD_CASHDRAWER = b"\x1b\x70\x00\x19\xfa"
# ESC @ — initialize printer (resets all modes to power-on defaults)
# Prepended to every job so printer state from a previous job never bleeds through.
_CMD_INIT = b"\x1b\x40"
# DLE ENQ 2 — real-time request: clear both the input data buffer and the
# print buffer.  Used by reset_printer() to unwedge an overflowed printer.
_CMD_CLEAR_BUFFERS = b"\x10\x05\x02"
# PP6800 font A: 42 chars/line (tested; pixel width controlled by print_width in supported_devices.py)
_RECEIPT_LINE_WIDTH = 42

# ─── Print pacing (buffer flow-control) ──────────────────────────────────────
# The JSON receipt path is fire-and-forget: a ~2 KB job drains to the printer's
# input buffer in ~0.2 s, far faster than the head prints it.  The PP6800 buffer
# holds only ~6 small receipts, so a batch of 7+ overflows it and drops receipts.
# The old raster path never hit this because its 56 KB image took ~4.86 s to
# transfer, which paced the printer for free.
#
# To restore that flow-control every JSON job is funnelled through a single
# drain worker that serialises writes and applies one of three runtime-tunable
# strategies (pace / chunked / status_poll, see PrintSettings) so the next job
# cannot refill the buffer until the previous receipt has mostly printed.  This
# caps in-buffer occupancy at ~1 receipt regardless of batch size.  An explicit,
# drainable queue also makes overflow recoverable: clear_queue()/reset_printer()
# can flush pending jobs and clear the printer buffer so a jam never blocks
# future prints.


class PrinterPool:
    """Singleton managing one persistent ESC/POS serial connection."""

    def __init__(
        self,
        device_key: str,
        settings: Optional[PrintSettings] = None,
    ) -> None:
        self._device_key = device_key
        self._helper: Optional[EscPosHelper] = None
        self._lock: Optional[asyncio.Lock] = None
        self._last_status: dict = {"is_online": None, "paper_status": "unknown"}
        self._last_write_error: Optional[str] = None
        self._settings = settings or PrintSettings()
        self._queue: Optional[asyncio.Queue] = None
        self._worker_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------ #
    # Lock / queue — created lazily inside the running event loop          #
    # ------------------------------------------------------------------ #

    @property
    def _async_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    @property
    def _job_queue(self) -> "asyncio.Queue":
        if self._queue is None:
            self._queue = asyncio.Queue()
        return self._queue

    # ------------------------------------------------------------------ #
    # Runtime settings                                                     #
    # ------------------------------------------------------------------ #

    def get_settings(self) -> PrintSettings:
        """Return the current (live) print settings."""
        return self._settings

    def update_settings(self, **partial) -> PrintSettings:
        """Apply a partial settings update with range validation.

        Builds a fresh validated ``PrintSettings`` from the current values
        merged with ``partial`` (so out-of-range values raise pydantic's
        ``ValidationError``), then swaps it in atomically.
        """
        merged = {**self._settings.model_dump(), **partial}
        self._settings = PrintSettings(**merged)
        self.publish_settings_metrics()
        return self._settings

    def publish_settings_metrics(self) -> None:
        """Mirror the live Printer Tuning config into Prometheus gauges.

        Called at startup and on every settings change so the dashboard can
        show which strategy and parameters were active during a print session.
        """
        s = self._settings
        for name in _PRINT_STRATEGIES:
            print_strategy_active.labels(strategy=name).set(
                1 if s.strategy == name else 0
            )
        for name in (
            "pace_base_ms",
            "pace_per_line_ms",
            "chunk_size",
            "chunk_delay_ms",
            "status_poll_timeout_ms",
            "status_poll_interval_ms",
        ):
            print_setting.labels(setting=name).set(getattr(s, name))

    # ------------------------------------------------------------------ #
    # Connection management (sync — called from thread pool)              #
    # ------------------------------------------------------------------ #

    @property
    def devfile(self) -> str:
        h = self._helper or EscPosHelper(self._device_key)
        conf = h.device.conf if h.device else None
        # Network/emulated devices have no devfile (host/port instead); fall
        # back to the conventional serial path so callers never crash.
        return getattr(conf, "devfile", None) or "/dev/ttyACM0"

    @staticmethod
    def _flush(printer) -> None:
        """Drain the transport's write buffer if it supports flushing.

        pyserial devices expose ``flush()`` (tcdrain — block until the USB-CDC
        FIFO has serialised every byte to the printer UART), which is what paces
        the serial path.  An escpos ``Network`` device's ``device`` is a raw
        socket whose ``sendall`` already pushed the bytes, so there is nothing
        to flush — this is a no-op there.  Keeps the write path transport-
        agnostic without changing serial behaviour.
        """
        device = getattr(printer, "device", None)
        flush = getattr(device, "flush", None)
        if callable(flush):
            flush()

    def open(self) -> None:
        self._helper = EscPosHelper(self._device_key)
        self._helper.init_printer()
        # Publish the printer's configured input-buffer size so the dashboard
        # can show how close a batch comes to overflowing it (0 if unknown).
        device = self._helper.device
        printer_buffer_size_bytes.set(getattr(device, "buffer_size", None) or 0)
        self.publish_settings_metrics()
        logger.info("[PrinterPool] Serial port opened.")

    def _close(self) -> None:
        if self._helper is not None:
            try:
                self._helper.close_printer()
            except Exception:
                pass
            self._helper = None

    def _reconnect(self) -> None:
        logger.warning("[PrinterPool] Reconnecting…")
        self._close()
        self.open()

    def _ensure(self) -> EscPosHelper:
        if self._helper is None or not self._helper.has_printer():
            self.open()
        return self._helper

    # ------------------------------------------------------------------ #
    # Encode (sync, no serial I/O) — fast ~25 ms                         #
    # ------------------------------------------------------------------ #

    def _encode_receipt(self, receipt: str) -> bytes:
        """Convert base64 receipt image to ESC/POS bytes.  No serial access."""
        h = self._ensure()
        img = EscPosHelper.format_base64_to_image(receipt)
        logger.info(
            "[PrinterPool] receipt image: %dx%d mode=%s print_width=%s",
            img.width,
            img.height,
            img.mode,
            h.device.print_width if h.device else None,
        )
        # Crop blank rows at the top — Odoo renders the receipt HTML with CSS
        # padding that produces a white band before the header content.
        bbox = ImageOps.invert(img.convert("L")).getbbox()
        if bbox and bbox[1] > 0:
            img = img.crop((0, bbox[1], img.width, img.height))
            logger.info("[PrinterPool] cropped %d top-whitespace rows", bbox[1])
        if h.device and h.device.print_width and img.width != h.device.print_width:
            new_height = int(img.height * h.device.print_width / img.width)
            img = img.resize((h.device.print_width, new_height), Image.LANCZOS)
            logger.info("[PrinterPool] resized to: %dx%d", img.width, img.height)
        image_conf = (
            h.device.image_conf.model_dump(exclude_unset=True)
            if h.device and h.device.image_conf
            else {"impl": "bitImageColumn", "center": False}
        )
        image_conf = {**image_conf, "center": False}
        logger.info(
            "[PrinterPool] encoding %dx%d  impl=%s",
            img.width,
            img.height,
            image_conf.get("impl"),
        )
        d = Dummy()
        # Suppress "media.width.pixel not set, center has no effect" — the
        # Dummy encoder has no profile width; we already force center=False.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*media\\.width\\.pixel.*")
            d.image(img, **image_conf)
        d.cut(feed=True)
        output = d.output
        if image_conf.get("impl") == "bitImageColumn":
            # python-escpos 3.1 hardcodes ESC 3 n=16; patch only the first occurrence
            # (the actual ESC 3 command) — coincidental matches in column data must not
            # be touched.  n=21 ≈ 24/203 × 180: closest integer for 1/180" motion unit.
            output = output.replace(b"\x1b\x33\x10", b"\x1b\x33\x15", 1)
        # _CMD_INIT (ESC @) resets the printer's ESC/POS command parser to a
        # known state before the image data so no stale mid-command state
        # from a previous job corrupts the image stream.
        return _CMD_INIT + output

    # ------------------------------------------------------------------ #
    # Write (sync, serial I/O) — slow ~payload_bytes × 10 / baud         #
    # ------------------------------------------------------------------ #

    def _sync_raw_write(self, payload: bytes) -> None:
        """Write raw ESC/POS bytes to the serial port.  Retry once on error."""
        # Do NOT close/reopen before every write. The unconditional reconnect
        # caused the PP6800 firmware to flush its buffer and advance paper on
        # every USB disconnect, printing the tail of the previous job before
        # the new one started.  _CMD_INIT in the payload resets the parser
        # state without triggering a USB disconnect side-effect.
        for attempt in range(2):
            try:
                h = self._ensure()
                t0 = time.perf_counter()
                h.printer._raw(payload)
                # tcdrain: OS kernel buffer → USB device internal FIFO.
                # tcdrain on Linux USB-CDC/ACM blocks until the USB device
                # has serialised all bytes to the printer UART, so flush()
                # already provides the full drain wait.  No extra sleep needed.
                self._flush(h.printer)
                dur = time.perf_counter() - t0
                serial_write_duration_seconds.observe(dur)
                logger.info(
                    "[PrinterPool] serial_write=%.3fs  payload=%d bytes",
                    dur,
                    len(payload),
                )
                return
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    raise HwPrinterError(f"[PrinterPool] Write failed: {e}") from e

    def _sync_raw_write_chunked(
        self, payload: bytes, chunk_size: int, chunk_delay_s: float
    ) -> None:
        """Write the payload in ``chunk_size`` slices, sleeping between each.

        Bytes never arrive faster than the head prints, so the printer's input
        buffer occupancy stays bounded even within one large receipt.  Retries
        the whole write once (via reconnect) on the first error, like
        ``_sync_raw_write``.
        """
        for attempt in range(2):
            try:
                h = self._ensure()
                t0 = time.perf_counter()
                for start in range(0, len(payload), chunk_size):
                    h.printer._raw(payload[start : start + chunk_size])
                    self._flush(h.printer)
                    if chunk_delay_s > 0:
                        time.sleep(chunk_delay_s)
                dur = time.perf_counter() - t0
                serial_write_duration_seconds.observe(dur)
                logger.info(
                    "[PrinterPool] chunked_write=%.3fs  payload=%d bytes  chunk=%d",
                    dur,
                    len(payload),
                    chunk_size,
                )
                return
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    raise HwPrinterError(
                        f"[PrinterPool] Chunked write failed: {e}"
                    ) from e

    def _sync_wait_ready(self, timeout_s: float, interval_s: float) -> bool:
        """Poll the printer's in-band online status until ready or timeout.

        Uses ``is_online()`` (DLE EOT real-time status) rather than the DSR
        modem line so it works over both serial and network transports.
        Returns True once the printer reports ready, False on timeout.
        """
        deadline = time.perf_counter() + timeout_s
        while True:
            try:
                h = self._ensure()
                if h.printer.is_online():
                    return True
            except Exception as e:
                logger.debug("[PrinterPool] wait_ready poll error: %s", e)
            if time.perf_counter() >= deadline:
                logger.warning(
                    "[PrinterPool] status_poll timed out after %.1fs", timeout_s
                )
                return False
            time.sleep(interval_s)

    def _sync_reset(self) -> None:
        """Clear the printer's buffers and re-initialise it.

        Sends the real-time buffer-clear (DLE ENQ 2), then close/reopen the USB
        connection (the same hammer ``_sync_cut`` uses to force the printer back
        ONLINE) and ESC @ to reset the command parser.  Unwedges an overflowed
        printer so the next job starts from a clean state.
        """
        try:
            h = self._ensure()
            h.printer._raw(_CMD_CLEAR_BUFFERS)
            self._flush(h.printer)
        except Exception as e:
            logger.warning("[PrinterPool] buffer-clear failed: %s", e)
        self._reconnect()
        h = self._ensure()
        h.printer._raw(_CMD_INIT)
        self._flush(h.printer)

    def _sync_cut(self) -> None:
        # Close then reopen: USB reconnect handshake brings the printer back ONLINE.
        # A persistent open connection can leave the printer in OFFLINE state where
        # buffer commands are queued but never executed.
        self._close()
        for attempt in range(2):
            try:
                h = self._ensure()
                h.printer._raw(_CMD_INIT)
                h.printer.cut(feed=True)
                self._flush(h.printer)
                return
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    raise HwPrinterError(f"[PrinterPool] Cut failed: {e}") from e

    def _sync_cashdrawer(self) -> None:
        self._close()
        for attempt in range(2):
            try:
                h = self._ensure()
                h.printer._raw(_CMD_CASHDRAWER)
                self._flush(h.printer)
                return
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    raise HwPrinterError(
                        f"[PrinterPool] Cash drawer failed: {e}"
                    ) from e

    def _sync_status(self) -> dict:
        for attempt in range(2):
            try:
                h = self._ensure()
                is_online = h.printer.is_online()
                code = h.printer.paper_status()
                paper = {2: "ok", 1: "near_end", 0: "no_paper"}.get(code, "unknown")
                return {"is_online": is_online, "paper_status": paper}
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    logger.error("[PrinterPool] Status error: %s", e)
                    return {
                        "is_online": False,
                        "paper_status": "unknown",
                        "error": str(e),
                    }

    # ------------------------------------------------------------------ #
    # Queue + drain worker + strategies                                   #
    # ------------------------------------------------------------------ #

    def start_worker(self) -> None:
        """Start the long-lived drain worker (idempotent).

        Called once at app startup.  All queued jobs are written by this single
        coroutine, which guarantees ordering and gives clear/reset a single
        place to intervene.
        """
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._drain_worker())
            logger.info("[PrinterPool] Drain worker started.")

    async def _drain_worker(self) -> None:
        """Pull jobs off the queue and write them one at a time, forever."""
        queue = self._job_queue
        while True:
            payload, n_lines = await queue.get()
            print_queue_depth.set(queue.qsize())
            try:
                await self._write_with_strategy(payload, n_lines)
                print_jobs_total.labels(action="receipt", result="printed").inc()
            except Exception as e:
                self._last_write_error = str(e)
                print_jobs_total.labels(action="receipt", result="error").inc()
                print_overflow_events_total.labels(cause="write_error").inc()
                print_overflow_bytes_total.labels(cause="write_error").inc(
                    len(payload)
                )
                logger.error("[PrinterPool] Drain worker write error: %s", e)
            finally:
                queue.task_done()

    async def _write_with_strategy(self, payload: bytes, n_lines: int) -> None:
        """Write one job under the lock, applying the active pacing strategy.

        The pace sleep / status poll runs while the lock is held so the next
        queued job cannot start refilling the printer's input buffer until the
        current receipt has mostly printed.  ``get_full_status`` keeps returning
        cached status meanwhile (it short-circuits when the lock is held).
        """
        s = self._settings
        async with self._async_lock:
            if s.strategy == "chunked":
                await asyncio.to_thread(
                    self._sync_raw_write_chunked,
                    payload,
                    s.chunk_size,
                    s.chunk_delay_ms / 1000,
                )
            else:
                await asyncio.to_thread(self._sync_raw_write, payload)
            self._last_write_error = None

            if s.strategy == "pace":
                pace_s = (s.pace_base_ms + s.pace_per_line_ms * n_lines) / 1000
                if pace_s > 0:
                    await asyncio.sleep(pace_s)
            elif s.strategy == "status_poll":
                await asyncio.to_thread(
                    self._sync_wait_ready,
                    s.status_poll_timeout_ms / 1000,
                    s.status_poll_interval_ms / 1000,
                )

    def _enqueue(self, payload: bytes, n_lines: int = 0) -> None:
        """Append a write job to the drain queue (never blocks)."""
        self._job_queue.put_nowait((payload, n_lines))
        print_queue_depth.set(self._job_queue.qsize())

    # ------------------------------------------------------------------ #
    # Recovery                                                            #
    # ------------------------------------------------------------------ #

    def clear_queue(self) -> int:
        """Discard all pending jobs without printing them.  Returns the count."""
        queue = self._job_queue
        cleared = 0
        dropped_bytes = 0
        while True:
            try:
                payload, _ = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            queue.task_done()
            cleared += 1
            dropped_bytes += len(payload)
        if cleared:
            print_overflow_events_total.labels(cause="dropped").inc(cleared)
            print_overflow_bytes_total.labels(cause="dropped").inc(dropped_bytes)
            logger.warning("[PrinterPool] Cleared %d pending job(s).", cleared)
        print_queue_depth.set(queue.qsize())
        return cleared

    async def reset_printer(self) -> int:
        """Recover an overflowed printer: flush the queue and clear its buffers.

        Returns the number of pending jobs discarded.
        """
        cleared = self.clear_queue()
        async with self._async_lock:
            await asyncio.to_thread(self._sync_reset)
        logger.warning("[PrinterPool] Printer reset (%d job(s) dropped).", cleared)
        return cleared

    async def _background_write(self, payload: bytes) -> None:
        """Acquire the lock and write a one-off command (no pacing).

        Used by the raster fallback and the cash-drawer path, which are not
        part of the batched JSON receipt pipeline.  Errors are logged, not
        raised, so a failed background write never surfaces to the caller.
        """
        async with self._async_lock:
            try:
                await asyncio.to_thread(self._sync_raw_write, payload)
                self._last_write_error = None
            except Exception as e:
                self._last_write_error = str(e)
                logger.error("[PrinterPool] Background write error: %s", e)

    # ------------------------------------------------------------------ #
    # Async public API                                                     #
    # ------------------------------------------------------------------ #

    async def get_full_status(self) -> dict:
        """
        Return printer status.  If a write is in progress return the cached
        status immediately so status_json never blocks for 4+ seconds.
        """
        if self._async_lock.locked():
            return dict(self._last_status)
        async with self._async_lock:
            status = await asyncio.to_thread(self._sync_status)
            self._last_status = status
            return status

    async def print_receipt(self, receipt: str) -> bool:
        """
        Encode receipt (~25 ms) then start a fire-and-forget write task.
        Returns True as soon as encoding succeeds — before the serial write
        completes.  The serial write runs in the background and takes ~5 s
        at 115 200 baud.
        """
        payload = await asyncio.to_thread(self._encode_receipt, receipt)
        asyncio.create_task(self._background_write(payload))
        return True

    async def cut(self) -> bool:
        async with self._async_lock:
            await asyncio.to_thread(self._sync_cut)
            return True

    async def open_cashdrawer(self) -> bool:
        async with self._async_lock:
            await asyncio.to_thread(self._sync_cashdrawer)
            return True

    # ------------------------------------------------------------------ #
    # JSON receipt (ESC/POS text commands — ~2 KB vs ~56 KB raster)      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _fit_sz(text_len: int, max_sz: int, W: int) -> int:
        """Largest size level ≤ max_sz at which text_len chars fit in W columns.

        Uses _SZ_W to determine how many chars fit per size level so that
        Normal (double-height, same width as Small) never triggers a reduction.
        """
        for sz in range(max_sz, 0, -1):
            if text_len <= W // _SZ_W[sz]:
                return sz
        return 1

    @staticmethod
    def _wrap_row(left: str, right: str, w: int) -> list[str]:
        """Word-wrap a label/price row into w-char print lines.

        Only the left (label) wraps across as many lines as needed at full
        width w.  The right (price) is right-justified on the vertically
        centred label line — (N-1)//2 for N label lines — so it appears
        visually centred beside the wrapped label block.
        Font size never changes across lines.
        """
        last_w = max(1, w - len(right) - 1) if right else w

        # Pass 1: word-wrap label to full width to determine line count.
        chunks: list[str] = []
        remaining = left.strip()
        while remaining:
            if len(remaining) <= w:
                chunks.append(remaining)
                break
            chunk = remaining[:w]
            bp = chunk.rfind(" ")
            if bp <= 0:
                bp = w
            chunks.append(remaining[:bp].rstrip())
            remaining = remaining[bp:].lstrip()
        if not chunks:
            chunks = [""]

        # Price line: vertically centred index.
        pi = (len(chunks) - 1) // 2

        # If the centred line is too wide to fit the price, split it.
        if right and len(chunks[pi]) > last_w:
            piece = chunks[pi]
            sub = piece[:last_w]
            bp = sub.rfind(" ")
            if bp <= 0:
                bp = last_w
            rest = piece[bp:].lstrip()
            chunks[pi : pi + 1] = [piece[:bp].rstrip(), rest] if rest else [piece[:bp].rstrip()]

        # Build output: label only on all lines except pi, which gets the price.
        result: list[str] = []
        for i, chunk in enumerate(chunks):
            if i == pi and right:
                gap = w - len(chunk) - len(right)
                if gap < 1:
                    chunk = chunk[:last_w]
                    gap = 1
                result.append(chunk + " " * gap + right)
            else:
                result.append(chunk)
        return result

    # ESC t 19 — select CP858 code page (has € at 0xD5, superset of PC437)
    _CMD_CP858 = b"\x1b\x74\x13"

    @staticmethod
    def _txt(text: str) -> bytes:
        """Encode text as CP858 bytes (handles € and other Latin chars)."""
        return text.encode("cp858", errors="replace")

    def _encode_json_receipt(self, data: PrintReceiptJsonRequest) -> bytes:
        """Render the flat ``lines`` array from the DOM scan to ESC/POS bytes.

        Size levels (char_size 1-3):
          1 = Small:  1× wide, 1× tall, 42 chars/line
          2 = Normal: 1× wide, 2× tall, 42 chars/line (double-height glyphs)
          3 = Big:    2× wide, 2× tall, 21 chars/line

        The global ``char_size`` is a *maximum*. Each line auto-reduces its
        size level so text is never truncated.
        Dividers always print at level 1 (full 42-char width).
        Row lines (product/total pairs) are always printed bold.
        """
        d = Dummy()
        W = _RECEIPT_LINE_WIDTH
        sz = max(1, min(3, data.char_size))

        # Switch to CP858 so € encodes correctly (0xD5). _CMD_INIT resets to
        # PC437, so this must come first inside d.output (prepended after).
        d._raw(self._CMD_CP858)

        for line in data.lines:
            max_line_sz = 1 if line.pin else max(1, min(3, line.s * sz))

            if line.t == "div":
                ch = (line.dv or "-")[0]
                d.set(align="left", bold=False, width=1, height=1)
                d._raw(self._txt(ch * W + "\n"))

            elif line.t == "text":
                text = line.v or ""
                align = line.c or "left"
                actual_sz = self._fit_sz(len(text), max_line_sz, W)
                w = W // _SZ_W[actual_sz]
                d.set(
                    align=align,
                    bold=line.b,
                    width=_SZ_W[actual_sz],
                    height=_SZ_H[actual_sz],
                    custom_size=True,
                )
                d._raw(self._txt(text[:w] + "\n"))

            elif line.t == "row":
                left = line.l or ""
                right = line.r or ""
                actual_sz = max(1, min(3, max_line_sz))
                w = W // _SZ_W[actual_sz]
                # Row lines are always bold; label wraps to multiple lines
                # if needed, price right-justified on the centred label line.
                d.set(
                    align="left",
                    bold=True,
                    width=_SZ_W[actual_sz],
                    height=_SZ_H[actual_sz],
                    custom_size=True,
                )
                for row_line in self._wrap_row(left, right, w):
                    d._raw(self._txt(row_line + "\n"))

        if data.cut:
            d.cut(feed=True)

        return _CMD_INIT + d.output

    async def print_receipt_json(self, data: PrintReceiptJsonRequest) -> bool:
        """Encode structured receipt (~5 ms) then enqueue it for the drain worker.

        Returns immediately — never blocks Odoo, even if the printer is jammed:
        the queue absorbs the job and the active strategy paces the worker so a
        batch cannot overflow the printer's small input buffer.  An overflow is
        recoverable via ``clear_queue``/``reset_printer``.
        """
        t0 = time.perf_counter()
        payload = await asyncio.to_thread(self._encode_json_receipt, data)
        self._enqueue(payload, len(data.lines))
        if data.open_cashdrawer:
            self._enqueue(_CMD_CASHDRAWER)
        # API response time = encode + queue (not the hardware write, which the
        # drain worker does later).  Recorded here so it covers every caller —
        # the Odoo route, the test batch, and the individual-ticket path alike.
        print_duration_seconds.labels(action="print_receipt_json").observe(
            time.perf_counter() - t0
        )
        return True

    async def default_action(self, action: str, receipt: Optional[str] = None) -> bool:
        if action == "print_receipt":
            return await self.print_receipt(receipt)
        if action == "cut_receipt":
            return await self.cut()
        if action in ("cashbox", "cashdrawer"):
            return await self.open_cashdrawer()
        logger.warning("[PrinterPool] Unknown action: %s", action)
        return False

    @property
    def last_write_error(self) -> Optional[str]:
        return self._last_write_error
