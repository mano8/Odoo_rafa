"""Prometheus metrics registry for hw_proxy."""
from prometheus_client import Counter, Gauge, Histogram

# --- HTTP layer (populated by metrics_middleware in main.py) ---
http_requests_total = Counter(
    "hw_proxy_http_requests_total",
    "Total HTTP requests handled",
    ["method", "endpoint", "status_code"],
)
http_request_duration_seconds = Histogram(
    "hw_proxy_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# --- Print jobs ---
print_jobs_total = Counter(
    "hw_proxy_print_jobs_total",
    "Total print jobs processed",
    ["action", "result"],
)
print_duration_seconds = Histogram(
    "hw_proxy_print_duration_seconds",
    "API response time for a print request: encode + queue (not hardware write)",
    ["action"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
)
serial_write_duration_seconds = Histogram(
    "hw_proxy_serial_write_duration_seconds",
    "Actual serial-port write time (hardware floor = payload_bytes × 10 / baud)",
    buckets=[0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0],
)

# --- Print pipeline (queue + drain worker; real and emulated printers alike) ---
# jobs_printed / errors reuse print_jobs_total (action="receipt"), populated by
# the drain worker so they count every job regardless of source (Odoo, test
# batch, individual ticket) — not just the Odoo HTTP route.
print_queue_depth = Gauge(
    "hw_proxy_print_queue_depth",
    "Print jobs currently waiting in the drain queue (jobs_queued).",
)
print_overflow_events_total = Counter(
    "hw_proxy_print_overflow_events_total",
    "Print jobs lost — dropped via clear-queue/reset, or failed at write. "
    "The real printer cannot report a firmware buffer overflow, so this counts "
    "the losses hw_proxy can observe; with pacing it stays 0 (healthy).",
    ["cause"],
)
print_overflow_bytes_total = Counter(
    "hw_proxy_print_overflow_bytes_total",
    "Bytes of print payload lost (dropped via clear-queue/reset or write error).",
    ["cause"],
)
printer_buffer_size_bytes = Gauge(
    "hw_proxy_printer_buffer_size_bytes",
    "Configured input-buffer size of the active printer in bytes (0 if unknown).",
)

# --- Printer Tuning configuration (mirrors PrintSettings; refreshed on change) ---
# Lets the dashboard show which strategy/parameters were live during a session,
# so overflow/throughput can be correlated with the tuning in effect.
print_strategy_active = Gauge(
    "hw_proxy_print_strategy_active",
    "Active flow-control strategy: 1 for the selected strategy, 0 for the others.",
    ["strategy"],
)
print_setting = Gauge(
    "hw_proxy_print_setting",
    "Live print-pipeline tuning parameter value (per 'setting' label; *_ms are "
    "milliseconds, chunk_size is bytes).",
    ["setting"],
)

# --- Hardware gauges (refreshed on each status poll) ---
printer_online = Gauge(
    "hw_proxy_printer_online",
    "Printer online: 1=online, 0=offline or unknown",
)
printer_paper_ok = Gauge(
    "hw_proxy_printer_paper_ok",
    "Paper level ok: 1=ok, 0=near-end, empty, or unknown",
)

# --- Cash drawer ---
cashdrawer_operations_total = Counter(
    "hw_proxy_cashdrawer_operations_total",
    "Total cash drawer open attempts",
    ["result"],
)

# --- System ---
disk_free_bytes = Gauge(
    "hw_proxy_disk_free_bytes",
    "Free disk space in bytes",
    ["mountpoint"],
)

# --- UPS (populated by _ups_metrics_task; requires NUT/upsc on the host) ---
ups_battery_charge = Gauge(
    "hw_proxy_ups_battery_charge_percent",
    "UPS battery charge level (0–100 %)",
)
ups_battery_voltage = Gauge(
    "hw_proxy_ups_battery_voltage_volts",
    "UPS battery voltage",
)
ups_input_voltage = Gauge(
    "hw_proxy_ups_input_voltage_volts",
    "UPS input (mains) voltage",
)
ups_load = Gauge(
    "hw_proxy_ups_load_percent",
    "UPS output load (0–100 %)",
)
ups_online = Gauge(
    "hw_proxy_ups_online",
    "UPS on mains power: 1=OL, 0=on battery or unknown",
)
ups_on_battery = Gauge(
    "hw_proxy_ups_on_battery",
    "UPS running on battery: 1=OB, 0=on mains",
)
ups_low_battery = Gauge(
    "hw_proxy_ups_low_battery",
    "UPS low-battery flag: 1=LB (shutdown imminent), 0=ok",
)
