"""
Module for FastAPI dependency injection.
"""
from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates
from hw_status.core.config import settings


def https_url_for(
    request: Request,
    name: str,
    **path_params: Any
) -> str:
    """Add https for static routes"""
    http_url = request.url_for(name, **path_params)
    # Replace 'http' with 'https'
    return http_url.replace("http", "https", 1)


def get_templates():
    """
    Define Template directory
    and adds https_url_for to ensure static
    files served as https.
    """
    template = Jinja2Templates(directory=settings.TEMPLATES_BASE_PATH)
    template.env.globals["https_url_for"] = https_url_for
    return template