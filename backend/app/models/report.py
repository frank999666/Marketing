import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, executive
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    content = Column(JSONB, default={})  # Structured report data
    file_url = Column(String(500))  # URL to generated PDF
    status = Column(String(50), default="generated")  # generated, sent, archived
    generated_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="reports")
