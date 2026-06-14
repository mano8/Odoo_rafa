"""Headline regression proof for the receipt-drop fix, hardware-free.

Drives synthetic receipts through the :class:`PrinterEmulator` buffer model with
a deterministic fake clock and asserts the diagnosis and the fix:

* an **unpaced** burst overflows the small buffer and drops receipts;
* **pace**, **chunked** and **status_poll** each keep buffer occupancy bounded,
  so there is **zero overflow** and **all N jobs print**.

The fake clock makes "the head has printed for T seconds" explicit instead of
sleeping, so the test is fast and deterministic.  It models the hw_proxy drain
worker's behaviour (one job at a time, then the strategy's wait) against the
emulator rather than importing escpos, so it runs in CI with only pytest + PyYAML.
"""

from emulator.core import PrinterEmulator

# A small JSON-style receipt: text bytes terminated by a GS V cut (job delimiter).
_GS_V_CUT = b"\x1d\x56\x41"
_RECEIPT = b"R" * 2048 + _GS_V_CUT
_RECEIPT_LEN = len(_RECEIPT)

# Six receipts fit, the seventh overflows — the field-observed PP6800 cliff.
_BUFFER_SIZE = _RECEIPT_LEN * 6
_DRAIN_BPS = 11_520  # 115 200 baud / 10 bits per byte
# Wall-clock seconds the head needs to print one receipt.
_RECEIPT_PRINT_S = _RECEIPT_LEN / _DRAIN_BPS


class FakeClock:
    """Manually advanced monotonic clock."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make_emulator(clock: FakeClock, **overrides) -> PrinterEmulator:
    params = dict(
        buffer_size=_BUFFER_SIZE,
        drain_rate_bps=_DRAIN_BPS,
        overflow_behavior="drop",
        clock=clock,
    )
    params.update(overrides)
    return PrinterEmulator(**params)


def _drain_fully(clock: FakeClock, emulator: PrinterEmulator) -> None:
    """Advance time well past the point where the buffer must be empty."""
    clock.advance(_RECEIPT_PRINT_S * 100)
    assert emulator.pending_bytes == 0


# ── Diagnosis: an unpaced burst overflows ────────────────────────────────────


def test_unpaced_burst_overflows() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock)

    # Fire-and-forget: 10 receipts arrive back-to-back with no time to print.
    for _ in range(10):
        emulator.feed(_RECEIPT)

    assert emulator.overflow_events > 0
    _drain_fully(clock, emulator)
    # Dropped receipts never print: fewer than 10 jobs come out.
    assert emulator.jobs_printed < 10


# ── Fix: pace spaces writes so the buffer never overflows ────────────────────


def test_pace_prevents_overflow() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock)

    # The pace strategy waits ~one receipt's print time after each write.
    for _ in range(10):
        emulator.feed(_RECEIPT)
        clock.advance(_RECEIPT_PRINT_S)

    assert emulator.overflow_events == 0
    _drain_fully(clock, emulator)
    assert emulator.jobs_printed == 10


# ── Fix: chunked write keeps occupancy bounded within a job ──────────────────


def test_chunked_prevents_overflow() -> None:
    clock = FakeClock()
    # Tight buffer (1.5 receipts) — only chunked pacing can keep up.
    emulator = _make_emulator(clock, buffer_size=_RECEIPT_LEN * 3 // 2)

    chunk = 256
    chunk_print_s = chunk / _DRAIN_BPS
    for _ in range(10):
        for start in range(0, _RECEIPT_LEN, chunk):
            emulator.feed(_RECEIPT[start : start + chunk])
            clock.advance(chunk_print_s)

    assert emulator.overflow_events == 0
    _drain_fully(clock, emulator)
    assert emulator.jobs_printed == 10


# ── Fix: status_poll waits until the buffer has drained ──────────────────────


def test_status_poll_prevents_overflow() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock)

    poll_step_s = _RECEIPT_PRINT_S / 4
    for _ in range(10):
        emulator.feed(_RECEIPT)
        # Poll the in-band online status until the head is nearly caught up.
        for _ in range(100):
            assert emulator.feed(b"\x10\x04\x01")  # DLE EOT 1 → 1 status byte
            if emulator.pending_bytes <= _RECEIPT_LEN:
                break
            clock.advance(poll_step_s)

    assert emulator.overflow_events == 0
    _drain_fully(clock, emulator)
    assert emulator.jobs_printed == 10


# ── Recovery: DLE ENQ 2 clears a wedged buffer ───────────────────────────────


def test_clear_buffers_recovers_from_overflow() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock, overflow_behavior="go_offline")

    for _ in range(10):
        emulator.feed(_RECEIPT)
    assert emulator.overflow_events > 0
    assert emulator.online is False

    emulator.feed(b"\x10\x05\x02")  # DLE ENQ 2 → clear buffers, back online
    assert emulator.pending_bytes == 0
    assert emulator.online is True


# ── max_queued_jobs models the cliff as a job count ──────────────────────────


def test_max_queued_jobs_overflow() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock, buffer_size=10_000_000, max_queued_jobs=6)

    for _ in range(10):
        emulator.feed(_RECEIPT)

    # The 7th job exceeds the queued-job cap even though bytes would fit.
    assert emulator.overflow_events > 0


# ── status reply bytes match what python-escpos expects ──────────────────────


def test_status_byte_reflects_state() -> None:
    clock = FakeClock()
    emulator = _make_emulator(clock)
    online_ok = emulator.feed(b"\x10\x04\x01")
    assert online_ok and not (online_ok[0] & 0x08)  # online bit clear

    emulator.paper_status = "no_paper"
    paper = emulator.feed(b"\x10\x04\x04")
    assert paper and (paper[0] & 0x60) == 0x60  # no-paper bits set
