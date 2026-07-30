from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.commitment import CommitmentStatus


class CommitmentBase(BaseModel):
    description: str
    owner: str | None = None
    made_by: str | None = None
    deadline: datetime | None = None
    department: str | None = None
    status: CommitmentStatus = CommitmentStatus.PENDING
    context: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    ai_extracted: bool = False
    follow_up_date: datetime | None = None
    escalation_count: int = 0

class CommitmentCreate(CommitmentBase):
    owner_user_id: UUID | None = None
    meeting_id: UUID | None = None

class CommitmentUpdate(BaseModel):
    status: CommitmentStatus | None = None
    deadline: datetime | None = None
    owner: str | None = None
    owner_user_id: UUID | None = None
    follow_up_date: datetime | None = None

class CommitmentResponse(CommitmentBase):
    id: UUID
    owner_user_id: UUID | None
    meeting_id: UUID | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommitmentList(BaseModel):
    items: list[CommitmentResponse]
    total: int
    skip: int
    limit: int


class CommitmentStatusUpdate(BaseModel):
    status: CommitmentStatus
