import asyncio
import logging

from app.database import AsyncSessionLocal
from app.services.teams import sync_teams_messages
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='poll_teams', bind=True, max_retries=3)
def poll_teams(self):
    logger.info("Starting Teams polling task")

    async def run_async():
        async with AsyncSessionLocal() as db:
            count = await sync_teams_messages(db)
            logger.info(f"Persisted {count} new Teams message(s)")

    try:
        asyncio.run(run_async())
        logger.info("Completed Teams polling task")
    except Exception as exc:
        logger.error(f"Error in poll_teams: {exc}")
        raise self.retry(exc=exc, countdown=60)
