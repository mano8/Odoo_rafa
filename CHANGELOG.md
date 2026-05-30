<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased] — Secure branch

### Added

- **`make certs-status`** — prints expiry state for all leaf certs (Traefik TLS, Docker
  mTLS CA, Docker mTLS client) without making any changes. Safe to run from cron/monitoring.

- **`make certs-renew`** — auto-renews any leaf cert expiring within 30 days using mkcert.
  Restarts only Traefik (no Docker daemon restart needed for leaf renewal). Idempotent —
  safe to run on a schedule.

- **`make certs-force-renew`** — unconditionally regenerates all leaf certs. Use after a
  CA rotation or to test that the renewal path works end-to-end.

- **`make certs-rotate-ca`** — interactive-only CA rotation (`rotate_ca.sh`). Requires
  typing `ROTATE` to proceed. Stops the compose stack before deleting the CA (prevents a
  TLS mismatch window), regenerates all certs, restarts the Docker daemon, then brings
  the stack back up. Intentionally kept separate from `certs-renew` so it cannot be
  triggered automatically.

- **`renew_certs.sh`** (`docker-compose/scripts/`) — mkcert-based leaf cert renewal
  script. Supports `--status`, `--force`, and auto-check modes. CAROOT fixed at
  `/opt/Odoo_rafa/mkcert-ca`.

- **`rotate_ca.sh`** (`docker-compose/scripts/`) — manual-only CA rotation script with
  interactive confirmation gate.

- **`make monitoring-reload-prometheus`** — sends `SIGHUP` to Prometheus for
  zero-downtime config reload after editing `prometheus.yml`. Does not restart
  the container; scraping continues uninterrupted. (`--web.enable-lifecycle` is
  not set so the HTTP reload endpoint is disabled; SIGHUP is the correct path.)

- **`make monitoring-reload-grafana`** — restarts the Grafana container to pick
  up changes to `monitoring/grafana/provisioning/` or `dashboards/`. Required
  because Grafana has no hot-reload signal.

- **`make monitoring-reload`** — convenience shortcut that runs both of the
  above in sequence.

- **`make backup-volumes`** — disaster-recovery volume snapshot. Stops DB and Odoo
  (~30 s), archives `postgres/pgdata` and `odoo/data` (filestore) as gzip tarballs
  into `/opt/backups/odoo_rafa/<datetime>/`. Keeps the last 5 snapshots (oldest
  rotated automatically). Expected compressed size: ~120 MB per snapshot.

- **`make restore-volumes BACKUP=<path>`** — restores from a snapshot directory.
  Stops all stacks, performs a clean extract with uid/gid preserved
  (userns-remap compatible), re-applies `auto_chown_volumes.sh`, then restarts
  both stacks.

- **`hw_proxy` test print fix** — `GET /hw_proxy/system/print_ticket` (the
  "Imprimir Ticket de Prueba" button in hw_status) was performing only a paper
  cut with no printed content. It now sends a real test receipt through the full
  ESC/POS JSON pipeline before cutting.

- **`pos_json_printer` i18n** — session report section headers (`SOLD:`,
  `REFUNDED:`, `Payments:`, `Taxes:`, `Total:`, `Discount`) are now translated
  via Odoo's `_t()` mechanism. Spanish translations added to `i18n/es.po`.

### Fixed

- **`pos_json_printer` session report layout** — replaced DOM scanning for the
  Z-report with a direct `get_sale_details` RPC data builder. DOM scanning was
  unreliable because `xml:space="preserve"` embedded newlines in text nodes,
  corrupting line-length calculations. Product rows now split to two lines (label
  then qty×price right-aligned) only when the combined width exceeds the printer
  line width for the active char_size (`42` chars for size 1/2, `21` for size 3).

- **`pos_json_printer` hamburger "Print Report"** — `Navbar.showSaleDetails()`
  was bypassing the JSON printer path. Patched `Navbar.prototype.showSaleDetails`
  so both the hamburger menu and the close-session button route through the same
  JSON printing pipeline.

- **`hw_proxy` version** bumped to `0.0.3`.

- **`pos_json_printer` version** bumped to `18.0.0.17.0`.

---

## [0.1.0] — 2026-05-25 (initial tracked release)

### Added

- Full offline deployment support for `odoo_prod` + `monitoring` stacks
  (`OFFLINE=1` flag; all images and wheels vendored in `docker_offline/`).
- `monitoring-up`, `monitoring-down`, `monitoring-logs` Makefile targets.
- `create-networks` target ensuring `monitoring_shared` network exists before
  any stack starts.
- `update-hw-proxy` Makefile target for routine hw_proxy updates without
  touching the Docker stack.
- `update-odoo-addon` Makefile target for focused addon deploys.
- hw_status service logs panel and dynamic services status grid.
- hw_proxy Prometheus metrics endpoint (`/hw_proxy/metrics`).
- `pos_json_printer` addon: JSON receipt pipeline (DOM scan → structured lines →
  ESC/POS), font size selector (Small/Normal/Big), CP858 encoding for `€`.

### Fixed

- PostgreSQL pgdata ownership: `auto_chown_volumes.sh` had `[fiesta_db]=0`
  (root); corrected to `70` (Alpine postgres uid).
- Traefik Docker provider removed — was looping on API version mismatch (1.24
  vs ≥1.40). File provider already handles all routes statically.
- hw_proxy bound to `10.254.254.1:9002` only (management dummy interface);
  was previously listening on `0.0.0.0:9002` (exposed to LAN).
- hw_proxy wheelhouse downloads no longer specify `--python-version` so wheels
  match the deployment server's Python (3.12) rather than Docker's (3.11).
- `sudo make update-hw-proxy` git ownership: git now runs as invoking user, not
  root, avoiding `dubious ownership` errors.
- Prometheus scrape target updated to `10.254.254.1:9002` after hw_proxy bind
  address change.
