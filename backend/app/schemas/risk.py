from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.risk import RiskLikelihood, RiskSeverity, RiskStatus


class RiskBase(BaseModel):
    description: str
    category: str | None = None
    severity: RiskSeverity = RiskSeverity.MEDIUM
    likelihood: RiskLikelihood = RiskLikelihood.POSSIBLE
    owner: str | None = None
    status: RiskStatus = RiskStatus.OPEN
    mitigation_plan: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    ai_extracted: bool = False
    department: str | None = None
    deadline: datetime | None = None

class RiskCreate(RiskBase):
    owner_user_id: UUID | None = None

class RiskUpdate(BaseModel):
    status: RiskStatus | None = None
    severity: RiskSeverity | None = None
    likelihood: RiskLikelihood | None = None
    mitigation_plan: str | None = None
    owner: str | None = None
    owner_user_id: UUID | None = None
    deadline: datetime | None = None

class RiskResponse(RiskBase):
    id: UUID
    owner_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RiskList(BaseModel):
    items: list[RiskResponse]
    total: int
    skip: int
    limit: int
