from datetime import datetime
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.services.audit import log_action
from app.schemas.task import (
    TaskCreate,
    TaskProgressUpdate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter()

@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    owner_id: UUID | None = None,
    department: str | None = None,
    due_before: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List tasks with optional filters."""
    query = select(Task).where(
        or_(Task.owner_id == current_user.id, Task.assigned_to == current_user.id)
    )
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if owner_id:
        query = query.where(Task.owner_id == owner_id)
    if department:
        query = query.where(Task.department == department)
    if due_before:
        query = query.where(Task.due_date <= due_before)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create task."""
    new_task = Task(**task_in.model_dump(exclude={"owner_id"}), owner_id=current_user.id)
    if not new_task.assigned_to:
        new_task.assigned_to = current_user.id
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get("/kanban", response_model=Any)
async def get_kanban(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get tasks grouped by status for kanban board."""
    query = select(Task).where(Task.assigned_to == current_user.id)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    kanban = {"TODO": [], "IN_PROGRESS": [], "WAITING": [], "DONE": []}
    for task in tasks:
        status = task.status if task.status in kanban else "TODO"
        kanban[status].append(task)
        
    return kanban

@router.get("/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get overdue tasks."""
    now = datetime.now()
    query = select(Task).where(
        and_(
            Task.assigned_to == current_user.id,
            Task.due_date < now,
            Task.status != TaskStatus.DONE
        )
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/stats", response_model=dict)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Task statistics by department, priority, status."""
    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    by_status: dict = {}
    by_priority: dict = {}
    for t in tasks:
        status_key = t.status.value if hasattr(t.status, "value") else str(t.status)
        priority_key = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
        by_status[status_key] = by_status.get(status_key, 0) + 1
        by_priority[priority_key] = by_priority.get(priority_key, 0) + 1

    return {
        "total": len(tasks),
        "by_status": by_status,
        "by_priority": by_priority,
    }

@router.get("/waiting-for-me", response_model=list[TaskResponse])
async def waiting_for_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Tasks where current user is responsible."""
    query = select(Task).where(
        and_(Task.assigned_to == current_user.id, Task.status != TaskStatus.DONE)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/waiting-for-others", response_model=list[TaskResponse])
async def waiting_for_others(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Tasks assigned to others by current user."""
    query = select(Task).where(
        and_(
            Task.owner_id == current_user.id,
            Task.assigned_to != current_user.id,
            Task.status != TaskStatus.DONE
        )
    )
    result = await db.execute(query)
    return result.scalars().all()
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get task detail."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update task."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
        
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete task."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await db.delete(task)
    await db.commit()
    await log_action(db, current_user, "TASK_DELETE", "Task", task_id, {"title": task.title})
    return {"message": "Task deleted successfully"}

@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_status(
    task_id: UUID,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update status."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = status_update.status
    await db.commit()
    await db.refresh(task)
    return task

@router.put("/{task_id}/progress", response_model=TaskResponse)
async def update_progress(
    task_id: UUID,
    progress_update: TaskProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update progress percentage."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.progress = progress_update.progress
    await db.commit()
    await db.refresh(task)
    return task

@router.post("/{task_id}/escalate")
async def escalate_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Manually escalate task."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.priority = TaskPriority.CRITICAL
    task.is_escalated = True
    await db.commit()
    return {"message": "Task escalated"}

