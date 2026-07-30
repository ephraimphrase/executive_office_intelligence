from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    department: str | None = None
    status: TaskStatus = TaskStatus.TODO
    source_type: str | None = None
    source_id: str | None = None
    ai_extracted: bool = False
    dependencies: list[str] = []
    progress: int = 0
    escalation_rules: dict[str, Any] = {}
    notes: str | None = None

class TaskCreate(TaskBase):
    owner_id: UUID | None = None
    assigned_to: UUID | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    department: str | None = None
    status: TaskStatus | None = None
    assigned_to: UUID | None = None
    progress: int | None = None
    notes: str | None = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskProgressUpdate(BaseModel):
    progress: int

class TaskResponse(TaskBase):
    id: UUID
    owner_id: UUID
    assigned_to: UUID | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TaskList(BaseModel):
    items: list[TaskResponse]
    total: int
    skip: int
    limit: int
