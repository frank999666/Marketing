from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

VALID_SOCIAL_PLATFORMS = {"instagram", "tiktok", "twitter", "facebook", "linkedin"}


class ConnectRequest(BaseModel):
    platform: str
    auth_code: str
    redirect_uri: str

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_SOCIAL_PLATFORMS:
            raise ValueError(f"platform must be one of: {', '.join(sorted(VALID_SOCIAL_PLATFORMS))}")
        return v

    @field_validator("redirect_uri")
    @classmethod
    def validate_redirect_uri(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("redirect_uri must be a valid URL")
        if len(v) > 2000:
            raise ValueError("redirect_uri must be at most 2000 characters")
        return v


class SocialAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    platform: str
    username: Optional[str]
    profile_data: dict = {}
    connected_at: datetime
    last_synced: Optional[datetime]


class PublishRequest(BaseModel):
    post_id: UUID
    platforms: List[str]
    schedule_at: Optional[datetime] = None

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one platform is required")
        for p in v:
            if p not in VALID_SOCIAL_PLATFORMS:
                raise ValueError(f"Invalid platform: {p}")
        return v
