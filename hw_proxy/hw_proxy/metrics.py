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
