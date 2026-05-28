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
from typing import Optional

from escpos.printer import Dummy
from PIL import Image, ImageOps

from hw_proxy.core.exceptions import HwPrinterError
from hw_proxy.metrics import serial_write_duration_seconds
from hw_proxy.schemas.receipt import PrintReceiptJsonRequest
from hw_proxy.tools.pos_helper import EscPosHelper

logger = logging.getLogger("hw_proxy")

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
# PP6800 font A: 42 chars/line (tested; pixel width controlled by print_width in supported_devices.py)
_RECEIPT_LINE_WIDTH = 42


class PrinterPool:
    """Singleton managing one persistent ESC/POS serial connection."""

    def __init__(self, device_key: str) -> None:
        self._device_key = device_key
        self._helper: Optional[EscPosHelper] = None
        self._lock: Optional[asyncio.Lock] = None
        self._last_status: dict = {"is_online": None, "paper_status": "unknown"}
        self._last_write_error: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Lock — created lazily inside the running event loop                 #
    # ------------------------------------------------------------------ #

    @property
    def _async_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    # ------------------------------------------------------------------ #
    # Connection management (sync — called from thread pool)              #
    # ------------------------------------------------------------------ #

    @property
    def devfile(self) -> str:
        h = self._helper or EscPosHelper(self._device_key)
        return h.device.conf.devfile if h.device else "/dev/ttyACM0"

    def open(self) -> None:
        self._helper = EscPosHelper(self._device_key)
        self._helper.init_printer()
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
            else {"impl": "bitImageRaster", "center": False}
        )
        image_conf = {**image_conf, "center": False}
        # Threshold to 1-bit: avoids Floyd-Steinberg dithering artifacts on
        # JPEG receipts — text is high-contrast so a clean threshold is better.
        img = img.convert("L").point(lambda x: 255 if x > 200 else 0).convert("1")
        # Manually fragment into ≤255-row bands so GS v 0 yH is always 0.
        # PP6800 ignores yH; any band taller than 255 rows causes bad chars.
        # We crop here and pass fragment_height=32000 to image() so python-escpos
        # never calls its own split() — that avoids any library ordering issues.
        frag_h = image_conf.get("fragment_height", 240)
        enc_conf = {**image_conf, "fragment_height": 32000}
        n_frags = max(1, (img.height + frag_h - 1) // frag_h)
        logger.info(
            "[PrinterPool] encoding 1-bit %dx%d  frag_h=%d  n_frags=%d",
            img.width,
            img.height,
            frag_h,
            n_frags,
        )
        d = Dummy()
        # Suppress "media.width.pixel not set, center has no effect" — the
        # Dummy encoder has no profile width; we already force center=False.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*media\\.width\\.pixel.*")
            for y in range(0, img.height, frag_h):
                band = img.crop((0, y, img.width, min(y + frag_h, img.height)))
                d.image(band, **enc_conf)
        d.cut(feed=True)
        # _CMD_INIT (ESC @) resets the printer's ESC/POS command parser to a
        # known state before the image bands so no stale mid-command state
        # from a previous job corrupts the GS v 0 header.
        return _CMD_INIT + d.output

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
                h.printer.device.flush()
                # The USB-CDC/ACM device still has to drain its FIFO to the
                # printer UART at 115 200 baud (~4.86 s for 56 KB).  Sleep
                # while holding the lock so the next job never sends bytes
                # while the UART is still transmitting the current one.
                baud = getattr(h.printer.device, "baudrate", 115_200)
                time.sleep(len(payload) * 10 / baud)
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
                h.printer.device.flush()
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
                h.printer.device.flush()
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
                code = h.printer.paper_status()
                paper = {2: "ok", 1: "near_end", 0: "no_paper"}.get(code, "unknown")
                return {"is_online": code in (0, 1, 2), "paper_status": paper}
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
    # Background write task                                               #
    # ------------------------------------------------------------------ #

    async def _background_write(self, payload: bytes) -> None:
        """Acquire the lock and write.  Errors are logged, not raised."""
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
                actual_sz = self._fit_sz(len(left) + len(right) + 1, max_line_sz, W)
                w = W // _SZ_W[actual_sz]
                # Row lines (product name/price, totals) are always bold for
                # readability; the DOM scan bold flag is ignored here.
                d.set(
                    align="left",
                    bold=True,
                    width=_SZ_W[actual_sz],
                    height=_SZ_H[actual_sz],
                    custom_size=True,
                )
                gap = w - len(left) - len(right)
                if gap < 1:
                    left = left[: max(0, w - len(right) - 1)]
                    gap = 1
                d._raw(self._txt(left + " " * gap + right + "\n"))

        if data.cut:
            d.cut(feed=True)

        return _CMD_INIT + d.output

    async def print_receipt_json(self, data: PrintReceiptJsonRequest) -> bool:
        """Encode structured receipt (~5 ms) then fire-and-forget serial write."""
        payload = await asyncio.to_thread(self._encode_json_receipt, data)
        asyncio.create_task(self._background_write(payload))
        if data.open_cashdrawer:
            asyncio.create_task(self._background_write(_CMD_CASHDRAWER))
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
