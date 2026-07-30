import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class MeetingType(str, enum.Enum):
    BOARD = "BOARD"
    EXECUTIVE_COMMITTEE = "EXECUTIVE_COMMITTEE"
    DEPARTMENT = "DEPARTMENT"
    ONE_ON_ONE = "ONE_ON_ONE"
    EXTERNAL = "EXTERNAL"
    SITE_VISIT = "SITE_VISIT"

class MeetingStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class MeetingRecord(Base):
    __tablename__ = "meeting_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    meeting_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    location = Column(String, nullable=True)
    meeting_type = Column(Enum(MeetingType), nullable=False, default=MeetingType.DEPARTMENT)
    chairperson = Column(String, nullable=True)
    status = Column(Enum(MeetingStatus), nullable=False, default=MeetingStatus.SCHEDULED)
    
    agenda = Column(JSON, default=list)
    participants = Column(JSON, default=list)
    minutes = Column(Text, nullable=True)
    ai_minutes = Column(Text, nullable=True)
    
    action_items = Column(JSON, default=list)
    decision_items = Column(JSON, default=list)
    
    follow_up_date = Column(DateTime, nullable=True)
    next_meeting_date = Column(DateTime, nullable=True)
    
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    transcript = Column(Text, nullable=True)
    recording_url = Column(String, nullable=True)
    
    board_paper_required = Column(Boolean, default=False)
    board_paper_submitted = Column(Boolean, default=False)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    event = relationship("Event", foreign_keys=[event_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
