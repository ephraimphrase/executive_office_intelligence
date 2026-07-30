
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WhatsAppMessageResponse(BaseModel):
    id: UUID
    sender: str
    content: str
    received_at: datetime

    model_config = ConfigDict(from_attributes=True)
