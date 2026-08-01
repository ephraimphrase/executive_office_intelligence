import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    actor_email = Column(String, nullable=True)  # snapshot — survives the actor being deleted later

    action = Column(String, nullable=False, index=True)  # e.g. "LOGIN", "USER_ROLE_CHANGE", "DECISION_DELETE"
    resource_type = Column(String, nullable=True, index=True)  # "User", "Task", "Decision", ...
    resource_id = Column(String, nullable=True)

    details = Column(JSON, default=dict)  # arbitrary before/after or context, kept small
    ip_address = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    actor = relationship("User", foreign_keys=[actor_user_id])
