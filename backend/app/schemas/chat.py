from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str # user or assistant
    content: str
    timestamp: datetime = datetime.now(timezone.utc)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    sources_used: list[dict[str, Any]] = []
    conversation_id: str
