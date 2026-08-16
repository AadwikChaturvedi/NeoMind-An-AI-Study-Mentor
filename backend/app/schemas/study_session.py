"""
schemas/study_session.py
--------------------------
Request/response schemas for the Study Timer feature.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class StudySessionCreate(BaseModel):
    duration: float = Field(..., description="Session length in minutes")
    distractions: int = 0
    focus_score: float = 0.0


class StudySessionOut(BaseModel):
    id: int
    duration: float
    distractions: int
    focus_score: float
    created_at: datetime

    class Config:
        from_attributes = True
