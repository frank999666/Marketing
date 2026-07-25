from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


class AnalyticsOverview(BaseModel):
    total_followers: int = 0
    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0
    engagement_rate: float = 0.0
    followers_change: int = 0
    reach_change: float = 0.0
    platforms: List[dict] = []


class PlatformMetrics(BaseModel):
    platform: str
    followers: int = 0
    reach: int = 0
    impressions: int = 0
    engagement: int = 0
    top_posts: List[dict] = []


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    alert_type: str
    severity: str
    title: Optional[str]
    message: Optional[str]
    explanation: Optional[str]
    evidence: dict = {}
    suggested_actions: list = []
    acknowledged: bool
    created_at: datetime


class AnalyticsTrend(BaseModel):
    date: date
    value: int
    metric: str
