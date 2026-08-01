import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class WhatsAppMessageType(str, enum.Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    AUDIO = "AUDIO"
    OTHER = "OTHER"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wa_message_id = Column(String, unique=True, index=True, nullable=True)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False, default="")
    message_type = Column(Enum(WhatsAppMessageType), nullable=False, default=WhatsAppMessageType.TEXT)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    ai_summary = Column(Text, nullable=True)
    ai_meeting_requests = Column(JSON, default=list)
    ai_reschedule_requests = Column(JSON, default=list)
    ai_action_items = Column(JSON, default=list)
    ai_decisions = Column(JSON, default=list)
    ai_commitments = Column(JSON, default=list)
    ai_risks = Column(JSON, default=list)
    department_category = Column(String, nullable=True)
    processed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
