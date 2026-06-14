"""Regression tests for the runtime-tunable, recoverable print pipeline.

These guard the fix for the PP6800 dropping receipts when 7+ are printed in a
batch.  The JSON receipt path is fire-and-forget, so without flow-control it
shoves each ~2 KB job into the printer's small input buffer far faster than the
head prints it, overflowing the buffer.  Every JSON job is therefore funnelled
through a single drain worker that serialises writes and applies one of three
pacing strategies (pace / chunked / status_poll), and an explicit queue makes an
overflow recoverable (clear_queue / reset_printer).

The ``escpos`` dependency tree (barcode/qrcode/...) is not needed for this logic
and is unavailable offline in the test env, so it is stubbed in ``sys.modules``
before importing the module under test.
"""

import asyncio
import sys
import types
from time import perf_counter

import pytest
from pydantic import ValidationError

# ── Stub the escpos import chain before importing printer_pool ───────────────
if "escpos" not in sys.modules or not hasattr(
    sys.modules.get("escpos"), "_hw_proxy_test_stub"
):
    _escpos = types.ModuleType("escpos")
    _escpos._hw_proxy_test_stub = True
    _printer = types.ModuleType("escpos.printer")

    class _Stub:  # minimal stand-in; these tests never exercise it
        def __init__(self, *args, **kwargs):
            pass

    for _name in ("Dummy", "Usb", "Network", "Serial"):
        setattr(_printer, _name, type(_name, (_Stub,), {}))
    _escpos.printer = _printer
    sys.modules["escpos"] = _escpos
    sys.modules["escpos.printer"] = _printer

from hw_proxy.core import printer_pool as pp  # noqa: E402
from hw_proxy.core.printer_pool import PrinterPool  # noqa: E402
from hw_proxy.schemas.receipt import (  # noqa: E402
    PrintReceiptJsonRequest,
    ReceiptLine,
)

# Pace long enough to measure reliably, short enough to keep tests fast.
_PACE_MS = 50


@pytest.fixture
def anyio_backend() -> str:
    """Run anyio tests on the asyncio backend (per project convention)."""
    return "asyncio"


def _make_pool() -> PrinterPool:
    return PrinterPool(device_key="test")


def _request(n_lines: int, open_cashdrawer: bool = False) -> PrintReceiptJsonRequest:
    return PrintReceiptJsonRequest(
        lines=[ReceiptLine(t="text", v=f"line {i}") for i in range(n_lines)],
        char_size=1,
        cut=True,
        open_cashdrawer=open_cashdrawer,
    )


# ── Fake printer/helper for the sync-write strategy tests ────────────────────


class _FakeDevice:
    def flush(self) -> None:
        pass


class _FakePrinter:
    def __init__(self, online_after: int = 0) -> None:
        self.writes: list[bytes] = []
        self.device = _FakeDevice()
        self._online_calls = 0
        self._online_after = online_after

    def _raw(self, payload: bytes) -> None:
        self.writes.append(payload)

    def is_online(self) -> bool:
        ready = self._online_calls >= self._online_after
        self._online_calls += 1
        return ready


class _FakeHelper:
    def __init__(self, printer: _FakePrinter) -> None:
        self.printer = printer

    def has_printer(self) -> bool:
        return True


def _attach_fake(pool: PrinterPool, printer: _FakePrinter) -> None:
    """Make the pool's sync paths use ``printer`` and never touch real serial."""
    helper = _FakeHelper(printer)
    pool._ensure = lambda: helper  # type: ignore[assignment]
    pool._reconnect = lambda: None  # type: ignore[assignment]


# ── Settings validation (g) ──────────────────────────────────────────────────


def test_default_settings() -> None:
    pool = _make_pool()
    s = pool.get_settings()
    assert s.strategy == "pace"
    assert s.pace_base_ms == 800


def test_update_settings_partial() -> None:
    pool = _make_pool()
    s = pool.update_settings(strategy="chunked", chunk_size=128)
    assert s.strategy == "chunked"
    assert s.chunk_size == 128
    # Untouched fields keep their previous value.
    assert s.pace_base_ms == 800


def test_update_settings_rejects_out_of_range() -> None:
    pool = _make_pool()
    with pytest.raises(ValidationError):
        pool.update_settings(pace_base_ms=999_999)
    with pytest.raises(ValidationError):
        pool.update_settings(chunk_size=4)  # below the 16-byte floor
    # A rejected update must not mutate the live settings.
    assert pool.get_settings().pace_base_ms == 800


def test_update_settings_persists_via_callback() -> None:
    saved: list = []
    pool = PrinterPool(device_key="test", persist=saved.append)
    s = pool.update_settings(strategy="chunked", chunk_size=128)
    # The persist sink receives exactly the new live settings.
    assert saved == [s]


def test_rejected_update_does_not_persist() -> None:
    saved: list = []
    pool = PrinterPool(device_key="test", persist=saved.append)
    with pytest.raises(ValidationError):
        pool.update_settings(pace_base_ms=999_999)
    assert saved == []


# ── Enqueue (print_receipt_json) ─────────────────────────────────────────────


@pytest.mark.anyio
async def test_print_receipt_json_enqueues(monkeypatch) -> None:
    pool = _make_pool()
    monkeypatch.setattr(pool, "_encode_json_receipt", lambda data: b"encoded")

    assert await pool.print_receipt_json(_request(7)) is True

    assert pool._job_queue.qsize() == 1
    payload, n_lines = pool._job_queue.get_nowait()
    assert payload == b"encoded"
    assert n_lines == 7


@pytest.mark.anyio
async def test_print_receipt_json_enqueues_cashdrawer(monkeypatch) -> None:
    pool = _make_pool()
    monkeypatch.setattr(pool, "_encode_json_receipt", lambda data: b"encoded")

    await pool.print_receipt_json(_request(3, open_cashdrawer=True))

    assert pool._job_queue.qsize() == 2
    assert pool._job_queue.get_nowait()[0] == b"encoded"
    assert pool._job_queue.get_nowait()[0] == pp._CMD_CASHDRAWER


# ── Worker drains one-by-one + pace spaces writes (a, b) ─────────────────────


@pytest.mark.anyio
async def test_worker_drains_and_paces(monkeypatch) -> None:
    pool = _make_pool()
    pool.update_settings(strategy="pace", pace_base_ms=_PACE_MS, pace_per_line_ms=0)
    write_times: list[float] = []
    monkeypatch.setattr(
        pool, "_sync_raw_write", lambda payload: write_times.append(perf_counter())
    )

    pool.start_worker()
    for _ in range(3):
        pool._enqueue(b"x", 0)
    await pool._job_queue.join()

    assert len(write_times) == 3
    gaps = [write_times[i + 1] - write_times[i] for i in range(2)]
    # Each successive write waits for the previous job's pace to elapse, so the
    # printer never receives more than one receipt at a time.
    assert all(gap >= (_PACE_MS / 1000) * 0.9 for gap in gaps)


# ── Chunked strategy writes all slices with gaps (c) ─────────────────────────


def test_chunked_write_slices_with_gaps(monkeypatch) -> None:
    pool = _make_pool()
    printer = _FakePrinter()
    _attach_fake(pool, printer)
    sleeps: list[float] = []
    monkeypatch.setattr(pp.time, "sleep", lambda s: sleeps.append(s))

    pool._sync_raw_write_chunked(b"abcdef", chunk_size=2, chunk_delay_s=0.01)

    assert printer.writes == [b"ab", b"cd", b"ef"]
    # A delay between every chunk paces the bytes to the head.
    assert sleeps == [0.01, 0.01, 0.01]


# ── status_poll waits until ready (d) ────────────────────────────────────────


def test_wait_ready_returns_when_online(monkeypatch) -> None:
    pool = _make_pool()
    printer = _FakePrinter(online_after=2)  # offline twice, then ready
    _attach_fake(pool, printer)
    monkeypatch.setattr(pp.time, "sleep", lambda s: None)

    assert pool._sync_wait_ready(timeout_s=1.0, interval_s=0.001) is True
    assert printer._online_calls == 3


def test_wait_ready_times_out(monkeypatch) -> None:
    pool = _make_pool()
    printer = _FakePrinter(online_after=10_000)  # never ready
    _attach_fake(pool, printer)
    monkeypatch.setattr(pp.time, "sleep", lambda s: None)

    assert pool._sync_wait_ready(timeout_s=0.0, interval_s=0.001) is False


# ── clear_queue empties pending jobs (e) ─────────────────────────────────────


@pytest.mark.anyio
async def test_clear_queue_discards_pending() -> None:
    pool = _make_pool()
    for _ in range(4):
        pool._enqueue(b"x", 0)

    assert pool.clear_queue() == 4
    assert pool._job_queue.qsize() == 0
    # A second clear on an empty queue is a no-op.
    assert pool.clear_queue() == 0


# ── reset_printer clears queue + issues buffer-clear/reconnect (f) ───────────


@pytest.mark.anyio
async def test_reset_printer_clears_and_recovers(monkeypatch) -> None:
    pool = _make_pool()
    for _ in range(3):
        pool._enqueue(b"x", 0)
    reset_calls: list[bool] = []
    monkeypatch.setattr(pool, "_sync_reset", lambda: reset_calls.append(True))

    cleared = await pool.reset_printer()

    assert cleared == 3
    assert pool._job_queue.qsize() == 0
    assert reset_calls == [True]


@pytest.mark.anyio
async def test_reset_aborts_in_flight_pace(monkeypatch) -> None:
    """reset_printer must not wait out the in-flight job's full pace delay.

    The worker holds the lock through the write and the pace sleep.  Without the
    interrupt, reset would block ~10 s behind the pace; the reset signal must
    abandon the sleep so reset returns near-instantly.
    """
    pool = _make_pool()
    pool.update_settings(strategy="pace", pace_base_ms=10_000, pace_per_line_ms=0)
    written = asyncio.Event()
    monkeypatch.setattr(pool, "_sync_raw_write", lambda payload: written.set())
    monkeypatch.setattr(pool, "_sync_reset", lambda: None)

    pool.start_worker()
    pool._enqueue(b"x", 0)
    # Wait until the worker has written the job and entered the 10 s pace,
    # holding the lock.
    await asyncio.wait_for(written.wait(), timeout=1.0)

    t0 = perf_counter()
    # If the pace were not interruptible this would block for ~10 s and the
    # wait_for would time out, failing the test.
    cleared = await asyncio.wait_for(pool.reset_printer(), timeout=3.0)
    assert perf_counter() - t0 < 2.0
    assert cleared == 0  # the only job was already in flight, not pending
    # The signal is cleared again so later jobs pace normally.
    assert pool._reset_signal.is_set() is False


def test_sync_reset_sequence(monkeypatch) -> None:
    pool = _make_pool()
    printer = _FakePrinter()
    reconnects: list[bool] = []
    helper = _FakeHelper(printer)
    pool._ensure = lambda: helper  # type: ignore[assignment]
    monkeypatch.setattr(pool, "_reconnect", lambda: reconnects.append(True))

    pool._sync_reset()

    # Buffer-clear, then (after a reconnect) re-initialise.
    assert printer.writes == [pp._CMD_CLEAR_BUFFERS, pp._CMD_INIT]
    assert reconnects == [True]
