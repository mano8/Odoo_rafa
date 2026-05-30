"""
Api routes for hw_status module
"""
import logging
import asyncio
import base64
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from escpos.printer import Dummy
from fastapi.templating import Jinja2Templates
from hw_status.tools.pos_helper import EscPosHelper
from hw_status.core.schemas import PrintRequest
from hw_status.core.deps import get_templates
from hw_status.core.config import settings

logger = logging.getLogger("hw_status")

router = APIRouter()


@router.get("/hello")
async def hello():
    """Emulates IoT Box hello endpoint"""
    return "ping"


def _detect_lang(accept_language: str) -> str:
    """Return 'es' if the browser prefers Spanish, 'en' otherwise."""
    for part in accept_language.split(","):
        lang = part.strip().split(";")[0].strip().lower()
        if lang.startswith("es"):
            return "es"
    return "en"


@router.get("/", response_class=HTMLResponse)
async def system_status(
    request: Request,
    lang: Optional[str] = Query(default=None),
    accept_language: str = Header(default=""),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Serves the IoT Box status UI in Spanish or English.

    Language priority: ?lang= query param > Accept-Language header.
    """
    resolved = lang if lang in ("es", "en") else _detect_lang(accept_language)
    template = "full_bootstrap_es.html" if resolved == "es" else "full_bootstrap.html"
    context = {
        "hw_proxy_url": str(settings.HW_PROXY_URL).rstrip("/"),
        "odoo_url": str(settings.BACKEND_HOST).rstrip("/"),
        "grafana_url": str(settings.BACKEND_HOST).rstrip("/") + "/grafana",
        "lang": resolved,
    }
    return templates.TemplateResponse(request=request, name=template, context=context)
