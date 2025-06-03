"""
"""

from pydantic import BaseModel


class JournalQuery(BaseModel):
    unit: str = "docker.service"
    since: str = None  # e.g. "5min", "2025-06-01T12:00:00"
    until: str = None
    