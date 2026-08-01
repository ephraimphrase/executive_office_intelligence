import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RiskSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskLikelihood(str, enum.Enum):
    VERY_LIKELY = "VERY_LIKELY"
    LIKELY = "LIKELY"
    POSSIBLE = "POSSIBLE"
    UNLIKELY = "UNLIKELY"

class RiskStatus(str, enum.Enum):
    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"
    ACCEPTED = "ACCEPTED"

class Risk(Base):
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    
    severity = Column(Enum(RiskSeverity), nullable=False, default=RiskSeverity.MEDIUM)
    likelihood = Column(Enum(RiskLikelihood), nullable=False, default=RiskLikelihood.POSSIBLE)
    
    owner = Column(String, nullable=True)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(Enum(RiskStatus), nullable=False, default=RiskStatus.OPEN)
    mitigation_plan = Column(Text, nullable=True)
    
    source_type = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    ai_extracted = Column(Boolean, default=False)
    
    department = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    owner_user = relationship("User", foreign_keys=[owner_user_id])
