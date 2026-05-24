"""
Module for FastAPI dependency injection.
"""
from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates
from hw_status.core.config import settings


class _NullCache:
    """No-op replacement for Jinja2's LRU cache.

    Jinja2 3.1.4 uses env.globals (a dict) as part of the cache key,
    making it unhashable. Replacing the cache with this object bypasses
    the key entirely. Fixed upstream in Jinja2 3.1.5.
    """

    def get(self, key: Any) -> None:
        return None

    def __setitem__(self, key: Any, value: Any) -> None:
        pass

    def __getitem__(self, key: Any) -> Any:
        raise KeyError(key)


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
    template.env.cache = _NullCache()
    return template