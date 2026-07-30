import asyncio
import logging
from datetime import date

from app.database import AsyncSessionLocal
from app.services.briefing import build_briefing_record
from app.services.briefing_generator import BriefingGeneratorService
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='generate_daily_briefing')
def generate_daily_briefing():
    logger.info("Starting daily briefing generation task")

    async def run_async():
        service = BriefingGeneratorService()
        today = date.today()

        async with AsyncSessionLocal() as db:
            pack = await service.generate_briefing(today, db)
            briefing = build_briefing_record(pack, today)
            db.add(briefing)
            await db.commit()
            await db.refresh(briefing)

            await service.export_to_docx(briefing, db)
            await service.send_briefing_email(briefing, ["gvp@dangote.com"])

    asyncio.run(run_async())
    logger.info("Completed daily briefing generation task")
