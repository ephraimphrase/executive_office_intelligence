from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeamsMessageResponse(BaseModel):
    id: UUID
    sender_name: str | None
    content: str
    received_at: datetime
    processed: bool

    model_config = ConfigDict(from_attributes=True)
