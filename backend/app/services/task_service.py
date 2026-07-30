import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.task import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)

_VALID_PRIORITIES = {p.value for p in TaskPriority}


class TaskService:
    async def create_task(self, task_data: dict, db) -> Task:
        task = Task(**task_data)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def update_task(self, task_id, task_data: dict, db) -> Task | None:
        task = await db.get(Task, task_id)
        if not task:
            return None
        for field, value in task_data.items():
            setattr(task, field, value)
        await db.commit()
        await db.refresh(task)
        return task

    async def get_tasks(self, db, filters: dict) -> list:
        query = select(Task)
        for field, value in (filters or {}).items():
            if value is not None and hasattr(Task, field):
                query = query.where(getattr(Task, field) == value)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_kanban(self, owner_id, db) -> dict:
        result = await db.execute(select(Task).where(Task.assigned_to == owner_id))
        kanban: dict = {"TODO": [], "IN_PROGRESS": [], "WAITING": [], "DONE": []}
        for task in result.scalars().all():
            status = task.status.value if hasattr(task.status, "value") else str(task.status)
            kanban.setdefault(status, []).append(task)
        return kanban

    async def check_overdue(self, db) -> list:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Task).where(Task.due_date < now, Task.status != TaskStatus.DONE)
        )
        return result.scalars().all()

    async def create_from_action_item(self, action_item: dict, source_type: str, source_id: str, owner_id, db) -> Task:
        priority = (action_item.get("priority") or "MEDIUM").upper()
        if priority not in _VALID_PRIORITIES:
            priority = "MEDIUM"

        due_date = None
        raw_deadline = action_item.get("deadline")
        if raw_deadline:
            try:
                from dateutil import parser as date_parser
                due_date = date_parser.parse(raw_deadline)
            except (ValueError, OverflowError):
                due_date = None

        description = action_item.get("description") or "Untitled task"
        task = Task(
            title=description[:250],
            description=description,
            owner_id=owner_id,
            assigned_to=owner_id,
            due_date=due_date,
            priority=priority,
            department=action_item.get("department"),
            source_type=source_type,
            source_id=source_id,
            ai_extracted=True,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def escalate_task(self, task_id, db) -> bool:
        task = await db.get(Task, task_id)
        if not task:
            return False
        task.priority = "CRITICAL"
        await db.commit()
        return True
