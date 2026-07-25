import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date, Time, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, tiktok, twitter, facebook, linkedin
    content_type = Column(String(50))  # post, reel, story, carousel, tweet, blog, newsletter
    title = Column(String(255))
    body = Column(Text)
    hashtags = Column(ARRAY(Text))
    media_urls = Column(JSONB, default=[])
    cta = Column(String(255))
    image_url = Column(String(500))
    status = Column(String(50), default="draft")  # draft, scheduled, published, failed
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    post_id_external = Column(String(255))  # ID del post en la plataforma externa
    metrics = Column(JSONB, default={})  # Métricas después de publicar
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="posts")
    calendar_entries = relationship("ContentCalendar", back_populates="post")


class ContentCalendar(Base):
    __tablename__ = "content_calendar"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    date = Column(Date, nullable=False)
    time = Column(Time)
    platform = Column(String(50))
    status = Column(String(50), default="planned")  # planned, scheduled, published, skipped
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="calendar_entries")
