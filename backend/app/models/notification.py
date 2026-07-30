import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationType(str, enum.Enum):
    MEETING_REMINDER = "MEETING_REMINDER"
    OVERDUE_TASK = "OVERDUE_TASK"
    CRITICAL_EMAIL = "CRITICAL_EMAIL"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    TRAVEL_ALERT = "TRAVEL_ALERT"
    WEATHER_ALERT = "WEATHER_ALERT"
    BOARD_MEETING = "BOARD_MEETING"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"
    COMMITMENT_DUE = "COMMITMENT_DUE"
    RISK_ALERT = "RISK_ALERT"

class NotificationPriority(str, enum.Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(Enum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    reference_type = Column(String, nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    action_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="notifications")
