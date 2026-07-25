import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok, twitter
    objective = Column(String(100))  # awareness, traffic, conversions, leads
    budget = Column(Numeric(10, 2))
    daily_budget = Column(Numeric(10, 2))
    audience_config = Column(JSONB, default={})  # targeting rules
    status = Column(String(50), default="draft")  # draft, pending_approval, active, paused, completed
    approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="campaigns")
    creatives = relationship("AdCreative", back_populates="campaign")


class AdCreative(Base):
    __tablename__ = "ad_creatives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("ad_campaigns.id"), nullable=False)
    copy = Column(Text)
    headline = Column(String(255))
    description = Column(Text)
    image_url = Column(String(500))
    video_url = Column(String(500))
    cta = Column(String(100))  # shop_now, learn_more, sign_up, etc.
    variant = Column(String(10))  # A, B, C for A/B testing
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("AdCampaign", back_populates="creatives")
