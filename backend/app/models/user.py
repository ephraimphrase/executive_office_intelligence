"""
User model — includes hashed_password for dev-mode local auth.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN               = "ADMIN"
    GVP                 = "GVP"
    CHIEF_OF_STAFF      = "CHIEF_OF_STAFF"
    EXECUTIVE_ASSISTANT = "EXECUTIVE_ASSISTANT"
    PERSONAL_ASSISTANT  = "PERSONAL_ASSISTANT"
    DEPARTMENT_HEAD     = "DEPARTMENT_HEAD"
    BOARD_SECRETARIAT   = "BOARD_SECRETARIAT"
    READ_ONLY           = "READ_ONLY"


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email          = Column(String, unique=True, index=True, nullable=False)
    full_name      = Column(String, nullable=False)
    hashed_password= Column(String, nullable=True)          # nullable — SSO users have no password
    role           = Column(Enum(UserRole), nullable=False, default=UserRole.READ_ONLY)
    avatar_url     = Column(String, nullable=True)
    is_active      = Column(Boolean, default=True)
    microsoft_id   = Column(String, unique=True, index=True, nullable=True)
    department     = Column(String, nullable=True)
    phone          = Column(String, nullable=True)
    preferences    = Column(JSON, default=dict)

    # Local-login MFA (opt-in). Irrelevant for SSO users — Entra ID owns MFA
    # for that path via tenant Conditional Access policy, not app code.
    mfa_enabled      = Column(Boolean, default=False)
    mfa_secret       = Column(String, nullable=True)
    mfa_backup_codes = Column(JSON, default=list)  # hashed, single-use

    created_at     = Column(DateTime(timezone=True), default=_utcnow)
    updated_at     = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    last_login     = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
