import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    brand_config = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("UserCompany", back_populates="company")
    brand_profile = relationship("BrandProfile", back_populates="company", uselist=False)
    posts = relationship("Post", back_populates="company")
    social_accounts = relationship("SocialAccount", back_populates="company")
    campaigns = relationship("AdCampaign", back_populates="company")
    reports = relationship("Report", back_populates="company")
