"""
routes/analytics.py
-----------------------
Analytics endpoint: aggregates real study_sessions data for the
Analytics page's charts. All the actual math lives in
services/analytics_service.py — this route just fetches sessions and
hands them off.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.study_session import StudySession
from app.schemas.analytics import AnalyticsSummary
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    sessions = db.query(StudySession).all()

    return AnalyticsSummary(
        daily_study_hours=analytics_service.daily_study_hours(sessions),
        focus_trend=analytics_service.daily_avg_focus(sessions),
        productivity_trend=analytics_service.daily_avg_productivity(sessions),
        distraction_per_day=analytics_service.daily_distractions(sessions),
        distraction_stats=analytics_service.distraction_stats(sessions),
    )
