"""FastAPI Async IoT Box Proxy for Odoo (Printer)"""
import logging
from ipaddress import ip_address, ip_network
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import JSONResponse
from hw_status.__init__ import configure_logging
from hw_status.app.main import app_router
from hw_status.core.config import settings
from urllib.parse import urlparse


logging.basicConfig()
configure_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger("hw_status")


# Networks you trust
TRUSTED_NETWORKS = [
    ip_network("172.16.0.0/12"),
    ip_network("192.168.1.0/24"),
    ip_network("127.0.0.0/16")
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
    If an Origin header is present, parse its hostname, convert to IP,
    and check if it also lies in TRUSTED_NETWORKS.  If parsing fails,
    or it's not in a trusted range, return False.
    """
    if not origin:
        return True  # no Origin header—let it pass to IP‐check
    try:
        parsed = urlparse(origin)
        hostname = parsed.hostname
        if hostname is None:
            return False
        ip = ip_address(hostname)
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

# --- CORS Middleware for Dev (allow all) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=3600,  # cache preflight requests for 1 hour
)

app.mount(
    f"{settings.API_PREFIX}/static",
    StaticFiles(directory=settings.STATIC_BASE_PATH),
    name="static"
)

app.include_router(app_router, prefix=settings.API_PREFIX)
