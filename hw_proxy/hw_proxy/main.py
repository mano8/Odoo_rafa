"""FastAPI Async IoT Box Proxy for Odoo (Printer)"""
import asyncio
import logging
import socket
import time
from ipaddress import ip_address, ip_network
from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from hw_proxy.__init__ import configure_logging
from hw_proxy.app.main import app_router
from hw_proxy.core.config import settings
from hw_proxy.core.printer_pool import PrinterPool
from hw_proxy.metrics import http_request_duration_seconds, http_requests_total


logging.basicConfig()
configure_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger("hw_proxy")

# Networks you trust
TRUSTED_NETWORKS = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("127.0.0.0/8"),
]


def is_ip_allowed(client_ip: str) -> bool:
    """
    Return True if the given client_ip (e.g. "192.168.1.23") falls
    into any of our TRUSTED_NETWORKS.  Otherwise False.
    """
    try:
        ip = ip_address(client_ip)
    except ValueError:
        return False
    return any(ip in net for net in TRUSTED_NETWORKS)


def is_origin_allowed(origin: str) -> bool:
    """
    If an Origin header is present, resolve its hostname to an IP and
    check if it lies in TRUSTED_NETWORKS.  Handles both numeric IPs and
    hostnames like 'localhost'.
    """
    if not origin:
        return True  # no Origin header—let it pass to IP‐check
    try:
        parsed = urlparse(origin)
        hostname = parsed.hostname
        if hostname is None:
            return False
        try:
            ip = ip_address(hostname)
        except ValueError:
            ip = ip_address(socket.gethostbyname(hostname))
        return any(ip in net for net in TRUSTED_NETWORKS)
    except Exception:
        return False


# --- App Initialization ---
app = FastAPI(
    title="Odoo IoT Box Proxy (FastAPI Async)",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)


@app.middleware("http")
async def ip_and_origin_filter(request: Request, call_next):
    client_ip = request.client.host or ""
    origin = request.headers.get("origin", None)

    # --- Always log every request for debugging
    logger.debug(
        "[Incoming Request] path=%s  method=%s  client_ip=%s  origin=%s",
        request.url.path,
        request.method,
        client_ip,
        origin,
    )

    # --- 1.a) First, reject any client IP not in TRUSTED_NETWORKS
    if not is_ip_allowed(client_ip):
        logger.warning(
            "[ip_and_origin_filter] Rejected client IP %s (not in trust list)",
            client_ip,
        )
        return JSONResponse(
            {"detail": "Client IP not allowed"}, status_code=403
        )

    # --- 1.b) If there is an Origin header, also check it:
    if origin and not is_origin_allowed(origin):
        logger.warning(
            "[ip_and_origin_filter] Rejected origin=%s from client_ip=%s",
            origin,
            client_ip,
        )
        return JSONResponse(
            {"detail": "CORS origin not allowed"}, status_code=403
        )

    # --- At this point, IP (and optional Origin) are trusted → proceed
    return await call_next(request)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record HTTP request count and latency for every non-metrics request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    path = request.url.path
    if path != f"{settings.API_PREFIX}/metrics":
        http_requests_total.labels(
            method=request.method,
            endpoint=path,
            status_code=str(response.status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=path,
        ).observe(duration)
    return response


@app.get(f"{settings.API_PREFIX}/metrics", include_in_schema=False)
async def metrics_endpoint():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# CORSMiddleware runs before ip_and_origin_filter (outermost wrapper).
# Allow any private-network origin (mirrors TRUSTED_NETWORKS) so that
# the Odoo POS frontend (e.g. https://192.168.1.146:9000) can reach
# hw_proxy (https://192.168.1.146:9001) without a CORS preflight failure.
# ip_and_origin_filter is the real security gate (TRUSTED_NETWORKS check).
_trusted_origin_regex = (
    r"^https?://"
    r"(localhost"
    r"|127\.0\.0\.1"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r")(:\d+)?$"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=_trusted_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=3600,
)

@app.on_event("startup")
async def _startup() -> None:
    pool = PrinterPool(settings.PRINTER_KEY)
    try:
        await asyncio.to_thread(pool.open)
    except Exception as e:
        logger.warning("[Startup] Printer not available at boot: %s", e)
    app.state.printer_pool = pool
    logger.info("[Startup] Printer pool ready.")


app.mount(
    f"{settings.API_PREFIX}/static",
    StaticFiles(directory=settings.STATIC_BASE_PATH),
    name="static"
)

app.include_router(app_router, prefix=settings.API_PREFIX)
