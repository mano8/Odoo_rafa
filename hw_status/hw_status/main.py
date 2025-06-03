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
    ip_network("172.18.0.0/16"),
    ip_network("192.168.1.0/24"),
    ip_network("127.0.0.0/16")
]


def is_origin_allowed(origin: str) -> bool:
    try:
        parsed = urlparse(origin)
        hostname = parsed.hostname
        if hostname is None:
            logger.error(
                "[is_origin_allowed] Request from "
                f"hostname: {hostname} is not allowed"
            )
            return False
        ip = ip_address(hostname)
        result = any(ip in net for net in TRUSTED_NETWORKS)
        if result is False:
            logger.error(
                "[is_origin_allowed] Request from "
                f"hostname: {hostname} is not allowed"
            )
        logger.debug(
            f"[is_origin_allowed] Request from hostname: {hostname} Accepted."
        )
        return result
    except ValueError as e:
        logger.error(
            "[is_origin_allowed] Fatal Error: "
            f"Request rejected error: {str(e)}"
        )
        return False


# --- App Initialization ---
app = FastAPI(
    title="Odoo IoT Box Proxy (FastAPI Async)",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# --- CORS Middleware for Dev (allow all) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # cache preflight requests for 1 hour
)


@app.middleware("http")
async def cors_ip_filter(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and not is_origin_allowed(origin):
        return JSONResponse({
            "detail": "CORS origin not allowed"},
            status_code=403
        )
    return await call_next(request)

app.mount(
    f"{settings.API_PREFIX}/static",
    StaticFiles(directory=settings.STATIC_BASE_PATH),
    name="static"
)

app.include_router(app_router, prefix=settings.API_PREFIX)
