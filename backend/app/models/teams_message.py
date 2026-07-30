import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TeamsMessageSource(str, enum.Enum):
    CHAT = "CHAT"
    CHANNEL = "CHANNEL"


class TeamsMessage(Base):
    __tablename__ = "teams_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teams_message_id = Column(String, unique=True, index=True, nullable=True)
    source = Column(Enum(TeamsMessageSource), nullable=False, default=TeamsMessageSource.CHAT)
    chat_id = Column(String, nullable=True)
    team_id = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)

    sender_name = Column(String, nullable=True)
    sender_id = Column(String, nullable=True)
    content = Column(Text, nullable=False, default="")
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ai_summary = Column(Text, nullable=True)
    ai_meeting_requests = Column(JSON, default=list)
    ai_reschedule_requests = Column(JSON, default=list)
    ai_action_items = Column(JSON, default=list)
    ai_decisions = Column(JSON, default=list)
    ai_commitments = Column(JSON, default=list)
    ai_risks = Column(JSON, default=list)
    department_category = Column(String, nullable=True)
    processed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
