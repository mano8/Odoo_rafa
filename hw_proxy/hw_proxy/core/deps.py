"""
Module for FastAPI dependency injection.
"""
from typing import Any, TYPE_CHECKING
from fastapi import Request
from fastapi.templating import Jinja2Templates
from hw_proxy.core.config import settings

if TYPE_CHECKING:
    from hw_proxy.core.printer_pool import PrinterPool


def get_printer_pool(request: Request) -> "PrinterPool":
    """Return the application-level printer pool from app.state."""
    return request.app.state.printer_pool


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


def get_templates() -> Jinja2Templates:
    """Define Template directory."""
    template = Jinja2Templates(directory=settings.TEMPLATES_BASE_PATH)
    template.env.cache = _NullCache()
    return template