"""
schemas/report.py
--------------------
Response schema for the Reports page — both GET /reports/summary
(JSON, used by the page) and GET /reports/pdf (PDF download) are
built from the same summary data.
"""

from pydantic import BaseModel


class ReportSummary(BaseModel):
    total_study_hours: float
    average_focus_score: float
    distractions_this_week: int
    average_productivity_score: float
    sessions_logged: int
