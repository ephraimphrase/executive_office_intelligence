import asyncio
import logging

from app.database import AsyncSessionLocal
from app.services.knowledge_base import KnowledgeBaseService
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(name='sync_onedrive')
def sync_onedrive():
    logger.info("Starting onedrive indexing task")

    async def run_async():
        service = KnowledgeBaseService()
        async with AsyncSessionLocal() as db:
            count = await service.sync_onedrive(db)
            logger.info(f"Indexed {count} new document(s) from OneDrive")

    asyncio.run(run_async())
    logger.info("Completed onedrive indexing task")
