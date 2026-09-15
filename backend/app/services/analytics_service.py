"""
services/analytics_service.py
--------------------------------
Turns raw StudySession rows into the aggregated series and stats the
Analytics page displays. All grouping happens here in Python rather
than in SQL — simplest option at this data scale, and keeps the date
math in one readable place.

Note on "productivity score": this isn't a field stored in the
database. It's a derived metric — focus score penalized for
distractions — computed here so the formula lives in exactly one
place. Adjust PRODUCTIVITY_DISTRACTION_PENALTY if you want distractions
to weigh more or less heavily.
"""

from collections import defaultdict
from datetime import date, timedelta
from typing import List, Optional

from app.models.study_session import StudySession

PRODUCTIVITY_DISTRACTION_PENALTY = 3  # points subtracted per distraction


def compute_productivity_score(focus_score: float, distractions: int) -> float:
    score = focus_score - (distractions * PRODUCTIVITY_DISTRACTION_PENALTY)
    return max(0.0, min(100.0, score))


def _last_n_days(n: int = 7) -> List[date]:
    today = date.today()
    return [today - timedelta(days=offset) for offset in range(n - 1, -1, -1)]


def _group_by_day(sessions: List[StudySession]) -> dict:
    grouped = defaultdict(list)
    for s in sessions:
        grouped[s.created_at.date()].append(s)
    return grouped


def daily_study_hours(sessions: List[StudySession], days: int = 7) -> dict:
    grouped = _group_by_day(sessions)
    day_range = _last_n_days(days)
    values = [
        round(sum(s.duration for s in grouped.get(day, [])) / 60, 2)
        for day in day_range
    ]
    return {"labels": [d.strftime("%a") for d in day_range], "values": values}


def daily_avg_focus(sessions: List[StudySession], days: int = 7) -> dict:
    grouped = _group_by_day(sessions)
    day_range = _last_n_days(days)
    values: List[Optional[float]] = []
    for day in day_range:
        day_sessions = grouped.get(day)
        if not day_sessions:
            values.append(None)  # no sessions that day — a gap, not a 0
        else:
            values.append(round(sum(s.focus_score for s in day_sessions) / len(day_sessions), 1))
    return {"labels": [d.strftime("%a") for d in day_range], "values": values}


def daily_avg_productivity(sessions: List[StudySession], days: int = 7) -> dict:
    grouped = _group_by_day(sessions)
    day_range = _last_n_days(days)
    values: List[Optional[float]] = []
    for day in day_range:
        day_sessions = grouped.get(day)
        if not day_sessions:
            values.append(None)
        else:
            scores = [compute_productivity_score(s.focus_score, s.distractions) for s in day_sessions]
            values.append(round(sum(scores) / len(scores), 1))
    return {"labels": [d.strftime("%a") for d in day_range], "values": values}


def daily_distractions(sessions: List[StudySession], days: int = 7) -> dict:
    grouped = _group_by_day(sessions)
    day_range = _last_n_days(days)
    values = [sum(s.distractions for s in grouped.get(day, [])) for day in day_range]
    return {"labels": [d.strftime("%a") for d in day_range], "values": values}


def distraction_stats(sessions: List[StudySession]) -> dict:
    if not sessions:
        return {
            "total_distractions": 0,
            "average_per_session": 0.0,
            "sessions_logged": 0,
            "distraction_free_sessions": 0,
        }

    total = sum(s.distractions for s in sessions)
    return {
        "total_distractions": total,
        "average_per_session": round(total / len(sessions), 2),
        "sessions_logged": len(sessions),
        "distraction_free_sessions": sum(1 for s in sessions if s.distractions == 0),
    }
