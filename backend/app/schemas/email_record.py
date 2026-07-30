from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.email_record import EmailPriority, EmailStatus


class EmailRecordBase(BaseModel):
    message_id: str
    subject: str | None = None
    sender_email: str
    sender_name: str | None = None
    received_at: datetime
    body_preview: str | None = None
    full_body: str | None = None
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.UNREAD
    ai_summary: str | None = None
    ai_action_items: list[dict[str, Any]] = []
    ai_decisions: list[dict[str, Any]] = []
    ai_risks: list[dict[str, Any]] = []
    ai_commitments: list[dict[str, Any]] = []
    suggested_reply: str | None = None
    department_category: str | None = None
    has_attachments: bool = False
    attachment_names: list[str] = []
    outlook_message_id: str | None = None
    thread_id: str | None = None
    is_high_priority: bool = False

class EmailRecordCreate(EmailRecordBase):
    pass

class EmailRecordUpdate(BaseModel):
    status: EmailStatus | None = None
    priority: EmailPriority | None = None
    department_category: str | None = None
    ai_summary: str | None = None
    ai_action_items: list[dict[str, Any]] | None = None

class EmailRecordResponse(EmailRecordBase):
    id: UUID
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EmailRecordList(BaseModel):
    items: list[EmailRecordResponse]
    total: int
    skip: int
    limit: int
