import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class EventType(str, enum.Enum):
    MEETING = "MEETING"
    BOARD = "BOARD"
    TRAVEL = "TRAVEL"
    SITE_VISIT = "SITE_VISIT"
    CALL = "CALL"
    PERSONAL = "PERSONAL"
    OTHER = "OTHER"

class EventPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class EventStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class EventSourceType(str, enum.Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    TEAMS = "TEAMS"
    MANUAL = "MANUAL"
    CALENDAR = "CALENDAR"

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    
    event_type = Column(Enum(EventType), nullable=False, default=EventType.MEETING)
    priority = Column(Enum(EventPriority), nullable=False, default=EventPriority.MEDIUM)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.SCHEDULED)
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source_type = Column(Enum(EventSourceType), nullable=False, default=EventSourceType.MANUAL)
    source_id = Column(String, nullable=True)
    
    ai_confidence = Column(Float, nullable=True)
    preparation_required = Column(Text, nullable=True)
    attendees = Column(JSON, default=list)
    agenda = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    venue = Column(String, nullable=True)
    
    travel_required = Column(Boolean, default=False)
    board_paper_required = Column(Boolean, default=False)
    
    reminder_minutes = Column(Integer, default=15)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    
    outlook_event_id = Column(String, nullable=True, unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", backref="events")
