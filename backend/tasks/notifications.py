import asyncio
import logging

from app.database import AsyncSessionLocal
from app.services.notification_service import NotificationService
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='send_meeting_reminders')
def send_meeting_reminders():
    logger.info("Starting meeting reminder task")

    async def run_async():
        service = NotificationService()
        async with AsyncSessionLocal() as db:
            count = await service.send_upcoming_meeting_reminders(db)
            logger.info(f"Created {count} meeting reminder notification(s)")

    asyncio.run(run_async())
    logger.info("Completed meeting reminder task")

@celery.task(name='check_overdue_tasks')
def check_overdue_tasks():
    logger.info("Starting overdue tasks check")

    async def run_async():
        service = NotificationService()
        async with AsyncSessionLocal() as db:
            count = await service.check_overdue_tasks_notifications(db)
            logger.info(f"Created {count} overdue task notification(s)")

    asyncio.run(run_async())
    logger.info("Completed overdue tasks check")
