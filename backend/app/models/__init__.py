"""
SQLAlchemy Models Package
All models imported here so Base.metadata registers every table.
"""
from app.models.audit_log import AuditLog
from app.models.briefing import Briefing
from app.models.commitment import Commitment, CommitmentStatus
from app.models.decision import Decision, DecisionStatus
from app.models.document import Document, FileType
from app.models.email_record import EmailPriority, EmailRecord, EmailStatus
from app.models.event import (
    Event,
    EventPriority,
    EventSourceType,
    EventStatus,
    EventType,
)
from app.models.meeting_record import MeetingRecord, MeetingStatus, MeetingType
from app.models.notification import Notification, NotificationPriority, NotificationType
from app.models.risk import Risk, RiskLikelihood, RiskSeverity, RiskStatus
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.teams_message import TeamsMessage, TeamsMessageSource
from app.models.user import User, UserRole
from app.models.whatsapp import WhatsAppMessage, WhatsAppMessageType

__all__ = [
    "AuditLog",
    "Briefing",
    "Commitment",
    "CommitmentStatus",
    "Decision",
    "DecisionStatus",
    "Document",
    "EmailPriority",
    "EmailRecord",
    "EmailStatus",
    "Event",
    "EventPriority",
    "EventSourceType",
    "EventStatus",
    "EventType",
    "FileType",
    "MeetingRecord",
    "MeetingStatus",
    "MeetingType",
    "Notification",
    "NotificationPriority",
    "NotificationType",
    "Risk",
    "RiskLikelihood",
    "RiskSeverity",
    "RiskStatus",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "TeamsMessage",
    "TeamsMessageSource",
    "User",
    "UserRole",
    "WhatsAppMessage",
    "WhatsAppMessageType",
]
