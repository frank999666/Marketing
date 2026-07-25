from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

VALID_CAMPAIGN_PLATFORMS = {"instagram", "facebook", "tiktok", "twitter", "linkedin"}
VALID_OBJECTIVES = {"awareness", "traffic", "conversions", "leads", "engagement"}


class CampaignCreate(BaseModel):
    name: str
    platform: str
    objective: Optional[str] = "awareness"
    budget: Optional[Decimal] = None
    daily_budget: Optional[Decimal] = None
    audience_config: Optional[dict] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(v) > 200:
            raise ValueError("Name must be at most 200 characters")
        return v.strip()

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_CAMPAIGN_PLATFORMS:
            raise ValueError(f"platform must be one of: {', '.join(sorted(VALID_CAMPAIGN_PLATFORMS))}")
        return v

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_OBJECTIVES:
            raise ValueError(f"objective must be one of: {', '.join(sorted(VALID_OBJECTIVES))}")
        return v


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    name: str
    platform: str
    objective: Optional[str]
    budget: Optional[Decimal]
    daily_budget: Optional[Decimal]
    audience_config: dict = {}
    status: str
    approved: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime


class CampaignGenerateRequest(BaseModel):
    objective: str
    budget: Decimal
    target_audience: Optional[str] = None
    product_description: Optional[str] = None
    num_variations: int = 2

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str) -> str:
        if v not in VALID_OBJECTIVES:
            raise ValueError(f"objective must be one of: {', '.join(sorted(VALID_OBJECTIVES))}")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
        if v > 1000000:
            raise ValueError("Budget must be at most 1,000,000")
        return v

    @field_validator("target_audience")
    @classmethod
    def validate_target_audience(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError("target_audience must be at most 500 characters")
        return v

    @field_validator("product_description")
    @classmethod
    def validate_product_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 2000:
            raise ValueError("product_description must be at most 2000 characters")
        return v


class CampaignGenerateResponse(BaseModel):
    campaign: CampaignResponse
    creatives: List[dict]
    strategy_summary: str
