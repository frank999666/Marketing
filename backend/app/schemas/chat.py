from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 5000:
            raise ValueError("Message must be at most 5000 characters long")
        return v


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    response: str
    sources: List[str] = []
    suggestions: List[str] = []
    timestamp: datetime = None


class ReportRequest(BaseModel):
    report_type: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        allowed = {"daily", "weekly", "monthly", "executive"}
        if v not in allowed:
            raise ValueError(f"report_type must be one of: {', '.join(sorted(allowed))}")
        return v
