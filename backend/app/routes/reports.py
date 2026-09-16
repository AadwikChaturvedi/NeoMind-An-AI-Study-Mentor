"""
routes/reports.py
---------------------
Backs the Reports page:
  GET /reports/summary  - JSON, used by the page itself
  GET /reports/pdf      - the same data as a downloadable PDF

Both are built from the same compute_report_summary() call, so the
page and the PDF can never show different numbers.
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.study_session import StudySession
from app.schemas.report import ReportSummary
from app.services.reports_service import compute_report_summary, generate_report_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=ReportSummary)
def get_report_summary(db: Session = Depends(get_db)):
    sessions = db.query(StudySession).all()
    return compute_report_summary(sessions)


@router.get("/pdf")
def download_report_pdf(db: Session = Depends(get_db)):
    sessions = db.query(StudySession).all()
    summary = compute_report_summary(sessions)
    pdf_bytes = generate_report_pdf(summary)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="neomind-study-report.pdf"'},
    )
