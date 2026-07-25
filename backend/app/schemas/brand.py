from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class BrandProfileCreate(BaseModel):
    industry: Optional[str] = None
    tone: Optional[str] = None
    values: Optional[List[str]] = None
    target_audience: Optional[str] = None
    colors: Optional[dict] = None
    fonts: Optional[dict] = None
    logo_url: Optional[str] = None
    guidelines: Optional[str] = None


class BrandProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    industry: Optional[str]
    tone: Optional[str]
    values: Optional[List[str]]
    target_audience: Optional[str]
    colors: Optional[dict]
    fonts: Optional[dict]
    logo_url: Optional[str]
    guidelines: Optional[str]
    created_at: datetime
