import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.integrations.microsoft_graph import MicrosoftGraphClient
from app.models.email_record import EmailRecord
from app.services.email_processor import EmailProcessorService
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='poll_emails', bind=True, max_retries=3)
def poll_emails(self):
    logger.info("Starting email polling task")

    async def run_async():
        settings = get_settings()
        graph = MicrosoftGraphClient()
        processor = EmailProcessorService()

        since = (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z"
        emails = await graph.get_emails(settings.gvp_email, since, limit=50)

        async with AsyncSessionLocal() as db:
            count = 0
            for e in emails:
                message_id = e.get("id")
                if message_id:
                    existing = await db.execute(
                        select(EmailRecord).where(EmailRecord.message_id == message_id)
                    )
                    if existing.scalars().first():
                        continue
                await processor.process_and_store(e, db)
                count += 1
            logger.info(f"Persisted {count} new email(s)")

    try:
        asyncio.run(run_async())
        logger.info("Completed email polling task")
    except Exception as exc:
        logger.error(f"Error in poll_emails: {exc}")
        raise self.retry(exc=exc, countdown=60)
