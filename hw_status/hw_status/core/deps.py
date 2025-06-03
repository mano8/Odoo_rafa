"""
Module for FastAPI dependency injection.
"""
from fastapi.templating import Jinja2Templates
from hw_status.core.config import settings

def get_templates():
    """
    Define Template directory
    """
    return Jinja2Templates(directory=settings.TEMPLATES_BASE_PATH)