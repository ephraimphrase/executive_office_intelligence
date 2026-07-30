from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BriefingBase(BaseModel):
    date: date
    events_summary: dict[str, Any] = {}
    tasks_summary: dict[str, Any] = {}
    email_highlights: dict[str, Any] = {}
    pending_decisions: dict[str, Any] = {}
    travel_info: dict[str, Any] = {}
    weather_info: dict[str, Any] = {}
    risks_summary: dict[str, Any] = {}
    talking_points: list[str] = []
    suggested_priorities: list[str] = []
    critical_alerts: list[str] = []
    full_content: dict[str, Any] = {}
    word_file_url: str | None = None
    pdf_file_url: str | None = None
    sent_to: list[str] = []

class BriefingCreate(BriefingBase):
    pass

class BriefingUpdate(BaseModel):
    full_content: dict[str, Any] | None = None
    word_file_url: str | None = None
    pdf_file_url: str | None = None
    sent_at: datetime | None = None
    sent_to: list[str] | None = None

class BriefingResponse(BriefingBase):
    id: UUID
    generated_at: datetime | None
    sent_at: datetime | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BriefingList(BaseModel):
    items: list[BriefingResponse]
    total: int
    skip: int
    limit: int
