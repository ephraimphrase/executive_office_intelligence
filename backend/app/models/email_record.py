import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class EmailPriority(str, enum.Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class EmailStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    PROCESSED = "PROCESSED"
    ARCHIVED = "ARCHIVED"
    REPLIED = "REPLIED"

class EmailRecord(Base):
    __tablename__ = "email_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String, unique=True, index=True, nullable=False)
    subject = Column(String, nullable=True)
    sender_email = Column(String, nullable=False)
    sender_name = Column(String, nullable=True)
    
    received_at = Column(DateTime, nullable=False)
    body_preview = Column(Text, nullable=True)
    full_body = Column(Text, nullable=True)
    
    priority = Column(Enum(EmailPriority), nullable=False, default=EmailPriority.NORMAL)
    status = Column(Enum(EmailStatus), nullable=False, default=EmailStatus.UNREAD)
    
    ai_summary = Column(Text, nullable=True)
    ai_meeting_requests = Column(JSON, default=list)
    ai_reschedule_requests = Column(JSON, default=list)
    ai_action_items = Column(JSON, default=list)
    ai_decisions = Column(JSON, default=list)
    ai_risks = Column(JSON, default=list)
    ai_commitments = Column(JSON, default=list)
    suggested_reply = Column(Text, nullable=True)
    
    department_category = Column(String, nullable=True)
    has_attachments = Column(Boolean, default=False)
    attachment_names = Column(JSON, default=list)
    
    outlook_message_id = Column(String, nullable=True, unique=True, index=True)
    thread_id = Column(String, nullable=True)
    is_high_priority = Column(Boolean, default=False)
    
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
