"""
services/reports_service.py
------------------------------
Computes the overall summary numbers shown on the Reports page, and
builds the downloadable PDF from that same summary.

Unlike analytics_service.py (day-by-day trend series for charts), this
produces a small set of all-time / this-week totals. Reuses
compute_productivity_score from analytics_service.py so that formula
lives in exactly one place across the whole app.
"""

from datetime import datetime, timedelta
from typing import List

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.models.study_session import StudySession
from app.services.analytics_service import compute_productivity_score


def compute_report_summary(sessions: List[StudySession]) -> dict:
    if not sessions:
        return {
            "total_study_hours": 0.0,
            "average_focus_score": 0.0,
            "distractions_this_week": 0,
            "average_productivity_score": 0.0,
            "sessions_logged": 0,
        }

    total_minutes = sum(s.duration for s in sessions)
    avg_focus = sum(s.focus_score for s in sessions) / len(sessions)

    week_ago = datetime.utcnow() - timedelta(days=7)
    distractions_this_week = sum(
        s.distractions for s in sessions if s.created_at and s.created_at >= week_ago
    )

    avg_productivity = sum(
        compute_productivity_score(s.focus_score, s.distractions) for s in sessions
    ) / len(sessions)

    return {
        "total_study_hours": round(total_minutes / 60, 2),
        "average_focus_score": round(avg_focus, 1),
        "distractions_this_week": distractions_this_week,
        "average_productivity_score": round(avg_productivity, 1),
        "sessions_logged": len(sessions),
    }


def generate_report_pdf(summary: dict) -> bytes:
    """Builds a simple one-page PDF from the summary dict. Kept
    deliberately plain (no charts/images) — just a clean, printable
    snapshot of the same numbers shown on the page."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 30)
    pdf.cell(0, 12, "NeoMind AI - Study Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 130)
    pdf.cell(
        0, 8,
        f"Generated {datetime.utcnow().strftime('%B %d, %Y')}",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.ln(8)

    rows = [
        ("Total study hours", f"{summary['total_study_hours']} h"),
        ("Average focus score", f"{summary['average_focus_score']} / 100"),
        ("Distractions this week", str(summary["distractions_this_week"])),
        ("Average productivity score", f"{summary['average_productivity_score']} / 100"),
        ("Sessions logged", str(summary["sessions_logged"])),
    ]

    for label, value in rows:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(20, 20, 30)
        pdf.cell(90, 10, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 13)
        pdf.cell(0, 10, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(140, 140, 150)
    pdf.multi_cell(
        0, 6,
        "Productivity score is a derived metric (focus score adjusted for "
        "distractions), not a value stored directly in the database.",
    )

    return bytes(pdf.output())
