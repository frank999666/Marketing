from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

VALID_PLATFORMS = {"instagram", "tiktok", "twitter", "facebook", "linkedin"}
VALID_CONTENT_TYPES = {"post", "reel", "story", "carousel", "tweet", "thread", "blog", "newsletter"}


class PostCreate(BaseModel):
    platform: str
    content_type: Optional[str] = "post"
    title: Optional[str] = None
    body: Optional[str] = None
    hashtags: Optional[List[str]] = None
    cta: Optional[str] = None
    image_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of: {', '.join(sorted(VALID_PLATFORMS))}")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CONTENT_TYPES:
            raise ValueError(f"content_type must be one of: {', '.join(sorted(VALID_CONTENT_TYPES))}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError("Title must be at most 500 characters")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 10000:
            raise ValueError("Body must be at most 10000 characters")
        return v


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    platform: str
    content_type: Optional[str]
    title: Optional[str]
    body: Optional[str]
    hashtags: Optional[List[str]]
    media_urls: list = []
    cta: Optional[str]
    image_url: Optional[str]
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    metrics: dict = {}
    created_at: datetime


class ContentGenerateRequest(BaseModel):
    platform: str
    content_type: str = "post"
    topic: Optional[str] = None
    num_variations: int = 3
    include_image: bool = False
    image_prompt: Optional[str] = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of: {', '.join(sorted(VALID_PLATFORMS))}")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        if v not in VALID_CONTENT_TYPES:
            raise ValueError(f"content_type must be one of: {', '.join(sorted(VALID_CONTENT_TYPES))}")
        return v

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError("Topic must be at most 500 characters")
        return v

    @field_validator("num_variations")
    @classmethod
    def validate_num_variations(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("num_variations must be between 1 and 10")
        return v


class ContentGenerateResponse(BaseModel):
    variations: List[dict]
    image_url: Optional[str] = None
