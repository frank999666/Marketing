from typing import List
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.report import Report
from app.schemas.chat import ReportRequest
from app.api.auth import get_current_company
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(Report)
        .filter(Report.company_id == company.id)
        .order_by(Report.generated_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "report_type": r.report_type,
            "period_start": str(r.period_start),
            "period_end": str(r.period_end),
            "status": r.status,
            "generated_at": str(r.generated_at),
        }
        for r in reports
    ]


@router.post("/generate")
def generate_report(
    request: ReportRequest,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    today = date.today()

    if request.report_type == "daily":
        period_start = today - timedelta(days=1)
        period_end = today
    elif request.report_type == "weekly":
        period_start = today - timedelta(days=7)
        period_end = today
    elif request.report_type == "monthly":
        period_start = today - timedelta(days=30)
        period_end = today
    else:  # executive
        period_start = today - timedelta(days=90)
        period_end = today

    report_service = ReportService()
    report_data = report_service.generate(
        company=company,
        report_type=request.report_type,
        period_start=period_start,
        period_end=period_end,
        db=db,
    )

    report = Report(
        company_id=company.id,
        report_type=request.report_type,
        period_start=period_start,
        period_end=period_end,
        content=report_data,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": str(report.id),
        "report_type": report.report_type,
        "content": report.content,
        "period_start": str(report.period_start),
        "period_end": str(report.period_end),
    }


@router.get("/{report_id}")
def get_report(
    report_id: UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.company_id == company.id,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": str(report.id),
        "report_type": report.report_type,
        "content": report.content,
        "period_start": str(report.period_start),
        "period_end": str(report.period_end),
        "generated_at": str(report.generated_at),
    }
