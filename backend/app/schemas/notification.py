from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationPriority, NotificationType


class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    is_read: bool = False
    reference_type: str | None = None
    reference_id: UUID | None = None
    action_url: str | None = None

class NotificationCreate(NotificationBase):
    user_id: UUID

class NotificationUpdate(BaseModel):
    is_read: bool | None = None

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    read_at: datetime | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationList(BaseModel):
    items: list[NotificationResponse]
    total: int
    skip: int
    limit: int
