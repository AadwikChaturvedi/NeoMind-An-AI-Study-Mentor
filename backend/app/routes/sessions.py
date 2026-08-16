"""
routes/sessions.py
----------------------
CRUD-style endpoints for study sessions:
  POST /sessions  - save a new session
  GET  /sessions  - list all sessions

Reads/writes the same study_sessions table as routes/timer.py.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.study_session import StudySession
from app.schemas.session import SessionCreate, SessionOut

router = APIRouter(tags=["Sessions"])


@router.post("/sessions", response_model=SessionOut)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    session = StudySession(
        duration=payload.duration,
        distractions=payload.distractions,
        focus_score=payload.focus_score,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(StudySession).order_by(StudySession.created_at.desc()).all()
    # Rounded here, not in the database: duration/focus_score are stored as
    # floats (routes/timer.py can save fractional minutes), but this
    # endpoint's contract promises whole numbers.
    return [
        SessionOut(
            id=s.id,
            duration=round(s.duration),
            distractions=s.distractions,
            focus_score=round(s.focus_score),
            created_at=s.created_at,
        )
        for s in sessions
    ]
