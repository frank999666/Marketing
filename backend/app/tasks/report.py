from datetime import date, timedelta
from app.tasks.worker import celery_app
from app.database import SessionLocal
from app.models.company import Company
from app.models.report import Report
from app.services.reports import ReportService


@celery_app.task(name="app.tasks.report.generate_daily")
def generate_daily():
    db = SessionLocal()
    try:
        companies = db.query(Company).all()
        report_service = ReportService()

        for company in companies:
            today = date.today()
            period_start = today - timedelta(days=1)

            report_data = report_service.generate(
                company=company,
                report_type="daily",
                period_start=period_start,
                period_end=today,
                db=db,
            )

            report = Report(
                company_id=company.id,
                report_type="daily",
                period_start=period_start,
                period_end=today,
                content=report_data,
            )
            db.add(report)

        db.commit()
    finally:
        db.close()
