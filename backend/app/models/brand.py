import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), unique=True, nullable=False)
    industry = Column(String(100))
    tone = Column(String(100))  # profesional, casual, divertido, serio, inspirador
    values = Column(ARRAY(Text))
    target_audience = Column(Text)
    colors = Column(JSONB, default={})  # {primary: "#xxx", secondary: "#xxx", accent: "#xxx"}
    fonts = Column(JSONB, default={})   # {heading: "font-name", body: "font-name"}
    logo_url = Column(String(500))
    guidelines = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="brand_profile")
