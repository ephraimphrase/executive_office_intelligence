import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
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


class DecisionStatus(str, enum.Enum):
    PENDING_IMPLEMENTATION = "PENDING_IMPLEMENTATION"
    IN_PROGRESS = "IN_PROGRESS"
    IMPLEMENTED = "IMPLEMENTED"
    REVERSED = "REVERSED"
    DEFERRED = "DEFERRED"

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    
    made_by = Column(String, nullable=True)
    made_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    meeting_id = Column(UUID(as_uuid=True), nullable=True)
    
    decision_date = Column(DateTime, nullable=True)
    department = Column(String, nullable=True)
    
    status = Column(Enum(DecisionStatus), nullable=False, default=DecisionStatus.PENDING_IMPLEMENTATION)
    implementation_progress = Column(Integer, default=0) # 0-100
    implementation_notes = Column(Text, nullable=True)
    
    responsible_person = Column(String, nullable=True)
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    supporting_documents = Column(JSON, default=list) # List of doc IDs
    deadline = Column(DateTime, nullable=True)
    
    source_type = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    ai_extracted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    made_by_user = relationship("User", foreign_keys=[made_by_user_id])
    responsible_user = relationship("User", foreign_keys=[responsible_user_id])
