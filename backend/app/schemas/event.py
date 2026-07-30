from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.event import EventPriority, EventSourceType, EventStatus, EventType


class EventBase(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    location: str | None = None
    event_type: EventType = EventType.MEETING
    priority: EventPriority = EventPriority.MEDIUM
    status: EventStatus = EventStatus.SCHEDULED
    source_type: EventSourceType = EventSourceType.MANUAL
    source_id: str | None = None
    ai_confidence: float | None = None
    preparation_required: str | None = None
    attendees: list[dict[str, Any]] = []
    agenda: str | None = None
    notes: str | None = None
    venue: str | None = None
    travel_required: bool = False
    board_paper_required: bool = False
    reminder_minutes: int = 15
    is_recurring: bool = False
    recurrence_rule: str | None = None
    outlook_event_id: str | None = None

class EventCreate(EventBase):
    owner_id: UUID

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = None
    event_type: EventType | None = None
    priority: EventPriority | None = None
    status: EventStatus | None = None
    attendees: list[dict[str, Any]] | None = None
    agenda: str | None = None
    notes: str | None = None
    venue: str | None = None
    travel_required: bool | None = None
    board_paper_required: bool | None = None

class EventResponse(EventBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EventList(BaseModel):
    items: list[EventResponse]
    total: int
    skip: int
    limit: int
