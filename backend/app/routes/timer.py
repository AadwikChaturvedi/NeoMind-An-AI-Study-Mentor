# Study Timer endpoints (start/stop session)
"""
routes/timer.py
-------------------
Study Timer endpoint: receives a session's data once it's stopped
and saves it to the study_sessions table.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.study_session import StudySession
from app.schemas.study_session import StudySessionCreate, StudySessionOut

router = APIRouter(prefix="/api/timer", tags=["Study Timer"])


@router.post("/session", response_model=StudySessionOut)
def create_session(payload: StudySessionCreate, db: Session = Depends(get_db)):
    session = StudySession(
        duration=payload.duration,
        distractions=payload.distractions,
        focus_score=payload.focus_score,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
