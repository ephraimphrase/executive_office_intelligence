from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.decision import DecisionStatus


class DecisionBase(BaseModel):
    description: str
    context: str | None = None
    made_by: str | None = None
    decision_date: datetime | None = None
    department: str | None = None
    status: DecisionStatus = DecisionStatus.PENDING_IMPLEMENTATION
    implementation_progress: int = 0
    implementation_notes: str | None = None
    responsible_person: str | None = None
    supporting_documents: list[str] = []
    deadline: datetime | None = None
    source_type: str | None = None
    source_id: str | None = None
    ai_extracted: bool = False

class DecisionCreate(DecisionBase):
    made_by_user_id: UUID | None = None
    meeting_id: UUID | None = None
    responsible_user_id: UUID | None = None

class DecisionUpdate(BaseModel):
    status: DecisionStatus | None = None
    implementation_progress: int | None = None
    implementation_notes: str | None = None
    responsible_person: str | None = None
    responsible_user_id: UUID | None = None
    deadline: datetime | None = None
    department: str | None = None

class DecisionResponse(DecisionBase):
    id: UUID
    made_by_user_id: UUID | None
    meeting_id: UUID | None
    responsible_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DecisionList(BaseModel):
    items: list[DecisionResponse]
    total: int
    skip: int
    limit: int


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus
