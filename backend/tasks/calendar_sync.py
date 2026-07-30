import asyncio
import logging

from app.database import AsyncSessionLocal
from app.services.calendar_service import CalendarService
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='sync_calendar')
def sync_calendar():
    logger.info("Starting calendar sync task")

    async def run_async():
        service = CalendarService()
        async with AsyncSessionLocal() as db:
            await service.sync_from_outlook(db)

    asyncio.run(run_async())
    logger.info("Completed calendar sync task")
