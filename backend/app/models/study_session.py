"""
models/study_session.py
--------------------------
SQLAlchemy model for the "study_sessions" table.
"""

from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    duration = Column(Float, nullable=False)            # session length in minutes
    distractions = Column(Integer, default=0)           # count of distractions during session
    focus_score = Column(Float, default=0.0)            # productivity score, 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
