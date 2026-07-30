import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.models.notification import Notification, NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    async def create_notification(self, user_id, type: str, title: str, message: str,
                                   priority: str = NotificationPriority.NORMAL,
                                   reference_type: str | None = None, reference_id=None, db=None) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            priority=priority,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        logger.info(f"Notification created for {user_id}: {title}")
        return notification

    async def get_user_notifications(self, user_id, unread_only: bool, db) -> list:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)  # noqa: E712
        query = query.order_by(Notification.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def mark_read(self, notification_id, user_id, db) -> bool:
        notification = await db.get(Notification, notification_id)
        if not notification or notification.user_id != user_id:
            return False
        notification.is_read = True
        notification.read_at = datetime.now()
        await db.commit()
        return True

    async def mark_all_read(self, user_id, db) -> int:
        result = await db.execute(
            select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        )
        notifications = result.scalars().all()
        for n in notifications:
            n.is_read = True
            n.read_at = datetime.now()
        await db.commit()
        return len(notifications)

    async def send_upcoming_meeting_reminders(self, db) -> int:
        """Create MEETING_REMINDER notifications for events starting within 30 minutes."""
        from app.models.event import Event

        now = datetime.now()
        window_end = now + timedelta(minutes=30)
        result = await db.execute(
            select(Event).where(Event.start_datetime >= now, Event.start_datetime <= window_end)
        )
        events = result.scalars().all()

        count = 0
        for event in events:
            existing = await db.execute(
                select(Notification).where(
                    Notification.reference_type == "EVENT",
                    Notification.reference_id == event.id,
                    Notification.type == NotificationType.MEETING_REMINDER,
                )
            )
            if existing.scalars().first():
                continue
            await self.create_notification(
                user_id=event.owner_id,
                type=NotificationType.MEETING_REMINDER,
                title=f"Upcoming meeting: {event.title}",
                message=f"'{event.title}' starts at {event.start_datetime.strftime('%H:%M')}.",
                priority=NotificationPriority.HIGH,
                reference_type="EVENT",
                reference_id=event.id,
                db=db,
            )
            count += 1
        logger.info(f"Created {count} upcoming meeting reminder notifications")
        return count

    async def check_overdue_tasks_notifications(self, db) -> int:
        """Create OVERDUE_TASK notifications for tasks past their due date."""
        from app.models.task import Task, TaskStatus

        now = datetime.now()
        result = await db.execute(
            select(Task).where(Task.due_date < now, Task.status != TaskStatus.DONE)
        )
        tasks = result.scalars().all()

        count = 0
        for task in tasks:
            existing = await db.execute(
                select(Notification).where(
                    Notification.reference_type == "TASK",
                    Notification.reference_id == task.id,
                    Notification.type == NotificationType.OVERDUE_TASK,
                )
            )
            if existing.scalars().first():
                continue
            owner = task.assigned_to or task.owner_id
            await self.create_notification(
                user_id=owner,
                type=NotificationType.OVERDUE_TASK,
                title=f"Overdue task: {task.title}",
                message=f"'{task.title}' was due {task.due_date.strftime('%Y-%m-%d')}.",
                priority=NotificationPriority.HIGH,
                reference_type="TASK",
                reference_id=task.id,
                db=db,
            )
            count += 1
        logger.info(f"Created {count} overdue task notifications")
        return count
