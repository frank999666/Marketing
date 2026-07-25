from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    slug: Optional[str] = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: Optional[str]
    plan: str
    brand_config: dict = {}
    created_at: datetime
