import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, BigInteger, Boolean, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, tiktok, twitter, facebook
    account_id = Column(String(255))  # ID en la plataforma
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    username = Column(String(255))
    profile_data = Column(JSONB, default={})  # followers, profile pic, etc.
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime)

    company = relationship("Company", back_populates="social_accounts")
    analytics = relationship("AnalyticsSnapshot", back_populates="social_account")


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    social_account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id"))
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    metric_type = Column(String(50), nullable=False)  # followers, reach, impressions, engagement, likes, comments, shares
    metric_value = Column(BigInteger, default=0)
    snapshot_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    social_account = relationship("SocialAccount", back_populates="analytics")


class AnalyticsAlert(Base):
    __tablename__ = "analytics_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # reach_drop, engagement_drop, follower_loss, high_cpa, conversion_issue
    severity = Column(String(50), default="warning")  # info, warning, critical
    title = Column(String(255))
    message = Column(Text)
    explanation = Column(Text)  # Por qué ocurrió
    evidence = Column(JSONB, default={})  # Datos que respaldan la alerta
    suggested_actions = Column(JSONB, default=[])  # Acciones sugeridas
    data = Column(JSONB, default={})
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
