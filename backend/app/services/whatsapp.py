import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def verify_webhook(token: str) -> bool:
    from app.config import get_settings
    return token == get_settings().whatsapp_verify_token


async def process_incoming_message(payload: dict, db: AsyncSession):
    """Parse an inbound WhatsApp webhook payload, persist it, and run AI extraction."""
    from app.integrations.whatsapp import WhatsAppClient
    from app.models.whatsapp import WhatsAppMessage

    parsed = WhatsAppClient().parse_webhook_message(payload)
    if not parsed or not parsed.get("from_number"):
        return None

    if parsed.get("id"):
        existing = await db.execute(
            select(WhatsAppMessage).where(WhatsAppMessage.wa_message_id == parsed["id"])
        )
        if existing.scalars().first():
            return existing.scalars().first()

    received_at = datetime.now(timezone.utc)
    ts = parsed.get("timestamp")
    if ts:
        try:
            received_at = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (ValueError, OSError, TypeError):
            pass

    message = WhatsAppMessage(
        wa_message_id=parsed.get("id"),
        sender=parsed["from_number"],
        content=parsed.get("text") or "",
        received_at=received_at,
    )

    if message.content:
        try:
            from agents.email_agent import EmailIntelligenceAgent
            from app.integrations.openai_client import get_openai_client

            agent = EmailIntelligenceAgent(get_openai_client())
            analysis = await agent.analyze_email(
                subject="WhatsApp message",
                body=message.content,
                sender=message.sender,
                received_at=received_at.isoformat(),
            )
            message.ai_summary = analysis.get("summary")
            message.ai_meeting_requests = analysis.get("meeting_requests", [])
            message.ai_reschedule_requests = analysis.get("reschedule_requests", [])
            message.ai_action_items = analysis.get("action_items", [])
            message.ai_decisions = analysis.get("decisions", [])
            message.ai_commitments = analysis.get("commitments", [])
            message.ai_risks = analysis.get("risks", [])
            message.department_category = analysis.get("department")
        except Exception as e:
            logger.warning(f"WhatsApp AI analysis failed: {e}")
        message.processed = True

    db.add(message)
    await db.commit()
    await db.refresh(message)

    await _auto_create_and_reschedule(message, db)
    return message


async def _auto_create_and_reschedule(message, db) -> None:
    """Automatically update the schedule/task register from a WhatsApp message —
    meeting requests, action items, decisions/commitments/risks, and
    'move it to Friday'-style reschedules, all without manual data entry."""
    from app.services.calendar_service import get_gvp_owner_id
    from app.services.extraction_pipeline import apply_reschedules, auto_create_records

    owner_id = await get_gvp_owner_id(db)
    extracted = {
        "meeting_requests": message.ai_meeting_requests,
        "action_items": message.ai_action_items,
        "decisions": message.ai_decisions,
        "commitments": message.ai_commitments,
        "risks": message.ai_risks,
        "department": message.department_category,
    }
    await auto_create_records("WHATSAPP", str(message.id), extracted, owner_id, db)
    await apply_reschedules(message.ai_reschedule_requests, owner_id, db)


async def get_whatsapp_stats(db: AsyncSession) -> dict:
    from app.models.whatsapp import WhatsAppMessage

    result = await db.execute(select(WhatsAppMessage))
    messages = result.scalars().all()
    return {
        "total": len(messages),
        "processed": sum(1 for m in messages if m.processed),
        "with_meeting_requests": sum(1 for m in messages if m.ai_meeting_requests),
        "with_action_items": sum(1 for m in messages if m.ai_action_items),
    }
