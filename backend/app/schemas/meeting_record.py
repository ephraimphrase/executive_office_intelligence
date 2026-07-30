from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.meeting_record import MeetingStatus, MeetingType


class MeetingRecordBase(BaseModel):
    title: str
    meeting_date: date
    start_time: time | None = None
    end_time: time | None = None
    location: str | None = None
    meeting_type: MeetingType = MeetingType.DEPARTMENT
    chairperson: str | None = None
    status: MeetingStatus = MeetingStatus.SCHEDULED
    agenda: list[dict[str, Any]] = []
    participants: list[dict[str, Any]] = []
    minutes: str | None = None
    ai_minutes: str | None = None
    action_items: list[dict[str, Any]] = []
    decision_items: list[dict[str, Any]] = []
    follow_up_date: datetime | None = None
    next_meeting_date: datetime | None = None
    transcript: str | None = None
    recording_url: str | None = None
    board_paper_required: bool = False
    board_paper_submitted: bool = False

class MeetingRecordCreate(MeetingRecordBase):
    event_id: UUID | None = None
    created_by_id: UUID | None = None

class MeetingRecordUpdate(BaseModel):
    status: MeetingStatus | None = None
    minutes: str | None = None
    ai_minutes: str | None = None
    action_items: list[dict[str, Any]] | None = None
    decision_items: list[dict[str, Any]] | None = None
    board_paper_submitted: bool | None = None
    recording_url: str | None = None

class MeetingRecordResponse(MeetingRecordBase):
    id: UUID
    event_id: UUID | None
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MeetingRecordList(BaseModel):
    items: list[MeetingRecordResponse]
    total: int
    skip: int
    limit: int
