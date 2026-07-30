"""Compatibility shim — wraps EmailProcessorService for router."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.email_record import EmailRecord
from app.services.email_processor import EmailProcessorService

_svc = EmailProcessorService()

async def sync_outlook_emails(db: AsyncSession) -> int:
    """Pull new mail from Outlook, analyze it, and persist unseen messages. Returns count processed."""
    from app.config import get_settings
    from app.integrations.microsoft_graph import MicrosoftGraphClient

    settings = get_settings()
    client = MicrosoftGraphClient()
    emails = await client.get_emails(settings.gvp_email, since_datetime=None, limit=50)

    count = 0
    for e in emails:
        message_id = e.get("id")
        if message_id:
            existing = await db.execute(select(EmailRecord).where(EmailRecord.message_id == message_id))
            if existing.scalars().first():
                continue
        await _svc.process_and_store(e, db)
        count += 1
    return count

async def process_unprocessed_emails(db: AsyncSession) -> int:
    """Re-run AI processing on every EmailRecord not yet processed. Returns count processed."""
    result = await db.execute(select(EmailRecord).where(EmailRecord.processed_at.is_(None)))
    records = result.scalars().all()
    for record in records:
        await _svc.analyze_and_update(record, db)
    return len(records)

async def process_email_ai(email_id, db: AsyncSession):
    """Re-run AI processing on a single existing email."""
    record = await db.get(EmailRecord, email_id)
    if not record:
        return None
    return await _svc.analyze_and_update(record, db)

async def create_task_from_email(email: EmailRecord, action_item: dict, owner_id, db: AsyncSession):
    from app.services.task_service import TaskService
    task_svc = TaskService()
    return await task_svc.create_from_action_item(action_item, 'EMAIL', str(email.id), owner_id, db)

async def create_event_from_email(email: EmailRecord, meeting_data: dict, owner_id, db: AsyncSession):
    from app.services.calendar_service import CalendarService
    cal_svc = CalendarService()
    return await cal_svc.create_from_extraction(meeting_data, str(email.id), owner_id, db)
