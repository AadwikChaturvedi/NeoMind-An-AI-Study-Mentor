"""
schemas/session.py
---------------------
Request/response schemas for the /sessions endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    duration: int
    distractions: int
    focus_score: int


class SessionOut(BaseModel):
    id: int
    duration: int
    distractions: int
    focus_score: int
    created_at: datetime

    class Config:
        from_attributes = True
