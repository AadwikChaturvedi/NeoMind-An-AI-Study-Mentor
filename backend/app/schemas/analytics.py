"""
schemas/analytics.py
-----------------------
Response schema for GET /analytics/summary.
"""

from typing import List, Optional

from pydantic import BaseModel


class SeriesData(BaseModel):
    """A simple labeled series — maps directly onto a Chart.js dataset."""
    labels: List[str]
    values: List[Optional[float]]  # None = no sessions that day (gap in the line, not a 0)


class DistractionStats(BaseModel):
    total_distractions: int
    average_per_session: float
    sessions_logged: int
    distraction_free_sessions: int


class AnalyticsSummary(BaseModel):
    daily_study_hours: SeriesData
    focus_trend: SeriesData
    productivity_trend: SeriesData
    distraction_per_day: SeriesData
    distraction_stats: DistractionStats
