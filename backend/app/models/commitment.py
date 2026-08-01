import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CommitmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FULFILLED = "FULFILLED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"

class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    
    owner = Column(String, nullable=True)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    made_by = Column(String, nullable=True)
    
    deadline = Column(DateTime, nullable=True)
    department = Column(String, nullable=True)
    
    status = Column(Enum(CommitmentStatus), nullable=False, default=CommitmentStatus.PENDING)
    context = Column(Text, nullable=True)
    meeting_id = Column(UUID(as_uuid=True), nullable=True)
    
    source_type = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    ai_extracted = Column(Boolean, default=False)
    
    follow_up_date = Column(DateTime, nullable=True)
    escalation_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    owner_user = relationship("User", foreign_keys=[owner_user_id])
