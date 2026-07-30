"""Chat messages are stored in Redis/memory, not in a DB model.
   This stub exists for import compatibility."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class ChatMessage:
    id: UUID = field(default_factory=uuid4)
    role: str = "user"   # "user" | "assistant"
    content: str = ""
    conversation_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: UUID | None = None
