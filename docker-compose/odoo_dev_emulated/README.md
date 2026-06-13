# odoo_dev_emulated — full debug stack with the ESC/POS printer emulator

A complete copy of the [`odoo_dev_offline`](../odoo_dev_offline) stack (Odoo 18,
hw_proxy, hw_status, Prometheus, Grafana, Postgres) with **one** difference: there
is no real printer. The `emulated_printer` service stands in for the PP6800 over
TCP, so the whole individual-ticket print pipeline — Odoo batches, the print
queue/strategies, and the reset recovery — can be reproduced and tuned **without
hardware**.

Use this stack to reproduce the *6-ok / 7-breaks* receipt-drop cliff and to
validate every pacing strategy (`pace`, `chunked`, `status_poll`) and the
queue/reset recovery from the hw_status UI.

## What differs from odoo_dev_offline

- Adds an `emulated_printer` service (built from
  [`../../emulated_printer`](../../emulated_printer), TCP on `9100`).
- `hw_proxy_service` drops `privileged: true`, the `/dev/ttyACM0` device mapping,
  and the chmod CMD. It runs `PRINTER_KEY=EMULATED` and is pointed at the emulator
  via `EMULATED_PRINTER_HOST` / `EMULATED_PRINTER_PORT` in the compose
  `environment:` block (not the `.env` file — hw_proxy forbids unknown `.env`
  keys).
- `hw_status_service` runs `PRINTER_KEY=EMULATED`.
- Self-contained: Prometheus, Grafana, and the Odoo addons/config are local copies
  (mirrored from `../odoo_dev_offline`); the addons/config and mutable state
  (`postgres/pgdata`, `odoo/data`) are gitignored, the same as `odoo_dev_offline`.

## Ports

`9000` Odoo · `9002` hw_proxy · `8015` hw_status · `9090` Prometheus ·
`3001` Grafana · `9100` emulator.

These collide with `odoo_dev_offline` and the plain `../../emulated_printer`
stack, so **run only one stack at a time**.

## Usage

```bash
cp .env.example .env
cp hw_proxy.env.example hw_proxy.env
cp hw_status.env.example hw_status.env
# edit secrets/passwords as needed

docker compose up -d --build
```

Then:

- hw_status tuning UI: <http://localhost:8015>
- hw_proxy Swagger: <http://localhost:9002/hw_proxy/docs>
- Odoo: <http://localhost:9000>
- Grafana: <http://localhost:3001> (admin/admin)

### Reproduce the overflow and validate a fix

1. From Swagger or the hw_status Printer Tuning card, set the pace params to `0`
   to remove the brake, then `GET /hw_proxy/system/print_test_batch?count=15`.
2. Read the emulator log:
   `docker compose logs emulated_printer | grep status=` — expect
   `overflow_events > 0` and `jobs_printed < 15` (receipts dropped).
3. Restore `pace` (e.g. base 800 ms / per-line 30 ms), **Reset printer**, run the
   batch again — expect `overflow_events=0`, `jobs_printed=15`.
4. Repeat for `chunked` and `status_poll`.

> The emulator only advances its drain clock on input; trigger a `printer_status`
> read (or another small job) at the end to get a true post-drain snapshot.
