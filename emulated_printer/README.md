# emulated_printer — controllable ESC/POS printer emulator

A hardware-free stand-in for the Posiflex PP6800, used to reproduce the
"receipt drops on large batches" bug and validate every hw_proxy print-pacing
strategy without the real printer.

## Why

The PP6800 has a small **input buffer** that the print head drains at the
115 200-baud line speed. The JSON receipt path is fire-and-forget, so a batch of
7+ small receipts lands in the buffer far faster than it prints — the buffer
overflows and receipts are silently dropped (6 ok, 7 breaks). This emulator
models exactly that: bytes arrive instantly, the head drains the buffer at
`drain_rate_bps`, and the buffer overflows once it fills. With it you can
reproduce the cliff and confirm that `pace` / `chunked` / `status_poll` keep the
buffer bounded.

## Layout

| Path | Purpose |
|------|---------|
| `emulator/core.py` | Transport-agnostic state machine (buffer, drain, overflow, in-band status). |
| `emulator/tcp_server.py` | asyncio TCP adapter (default; clean across containers). |
| `emulator/pty_server.py` | socat/PTY + pyserial adapter (full serial fidelity). |
| `server.py` | CLI entrypoint: load a YAML profile, pick the transport. |
| `config/pp6800.yml` | Default profile — tune `buffer_size` / `drain_rate_bps` to the cliff. |
| `tests/test_overflow.py` | Hardware-free regression proof (pytest, no escpos). |
| `Dockerfile` / `docker-compose.yml` | Self-contained TCP stack: emulator + hw_proxy + hw_status. |
| `Dockerfile.serial` / `docker-compose.serial.yml` | Combined image for full serial fidelity (shared PTY). |
| `run_local.sh` / `start_serial.sh` | socat PTY launchers (run **inside** the container). |

## Run the test stack (no hardware, no Odoo)

```bash
cd emulated_printer
cp hw_proxy.env.example hw_proxy.env      # or use the provided hw_proxy.env
cp hw_status.env.example hw_status.env
docker compose up --build
```

- hw_status tuning UI: <http://localhost:8015>
- hw_proxy Swagger:     <http://localhost:9002/hw_proxy/docs>
- emulator TCP port:    `localhost:9100`

hw_proxy runs with `PRINTER_KEY=EMULATED` and talks to the emulator as an escpos
`Network` device. From the hw_status **Printer Tuning** card (or Swagger) you can:
set a strategy, fire `print_test_batch?count=N`, watch whether all N print, and
`reset_printer` to recover. The production `docker-compose/odoo_dev_offline`
stack is untouched — it keeps the real `/dev/ttyACM0` mapping.

### Per-strategy sweep

1. Set the strategy (`pace` / `chunked` / `status_poll`) and params, **Apply**.
2. `GET /system/print_test_batch?count=15&lines=20`.
3. Check the emulator container logs for `overflow_events` in the status line.
4. To reproduce the failure, set the pace params to 0 (no brake) and re-run —
   the emulator should report overflow and fewer than 15 jobs printed.

## Transports

- **TCP (default)** — the Docker stack path. Works cleanly across containers; no
  shared PTY. `status_poll` uses in-band `DLE EOT` status (not the DSR modem
  line), so it works over TCP.
- **Serial / PTY** — full escpos `Serial` fidelity. Windows has no `socat`, so
  this runs **inside the Linux container** only. PTYs can't be bridged across
  containers, so the serial variant combines the emulator and hw_proxy in one
  image (`Dockerfile.serial`); `socat` links one PTY end to `/dev/ttyACM0` and
  hw_proxy opens it with the unchanged PP6800 profile:

  ```bash
  docker compose -f emulated_printer/docker-compose.serial.yml up --build
  ```

## Profile (`config/pp6800.yml`)

Every characteristic is tunable: `buffer_size`, `drain_rate_bps`,
`max_queued_jobs`, `overflow_behavior` (`drop` / `truncate` / `garble` /
`go_offline`), `paper_status`, `online`. Tune until the emulator matches the
observed 6-ok / 7-breaks cliff — that calibrates the overflow model.

## Local tests

```bash
cd emulated_printer
python -m pytest tests/ -q
```
