"""
Api routes for hw_status module
"""
import logging
import asyncio
import base64
from fastapi import APIRouter, Depends, HTTPException, Header, Request
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


@router.get(
    "/",
    response_class=HTMLResponse
)
async def system_status(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Emulates IoT Box hello endpoint"""
    return templates.TemplateResponse(
        request=request,
        name="status.html",
        context={
            "base_url": str(request.base_url),
            "google_login_url": "",
            "hw_proxy_url": str(settings.HW_PROXY_URL).rstrip("/"),
            "odoo_url": str(settings.BACKEND_HOST).rstrip("/"),
        },
    )
