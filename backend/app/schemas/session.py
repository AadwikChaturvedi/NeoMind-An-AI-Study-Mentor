"""
schemas/session.py
---------------------
Request/response schemas for the /sessions endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    duration: int
    distractions: int
    focus_score: int


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    duration: int
    distractions: int
    focus_score: int
    created_at: datetime
