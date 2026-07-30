import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def sync_teams_messages(db: AsyncSession) -> int:
    """Poll the GVP's Teams chats for new messages, persist them, and run the
    same AI extraction pipeline as email/WhatsApp (meeting requests, action
    items, reschedules — auto-applied, no manual data entry)."""
    if db is None:
        return 0

    from dateutil import parser as date_parser

    from app.config import get_settings
    from app.integrations.microsoft_graph import MicrosoftGraphClient
    from app.models.teams_message import TeamsMessage

    settings = get_settings()
    graph = MicrosoftGraphClient()
    chats = await graph.list_chats(settings.gvp_email)

    count = 0
    for chat in chats:
        chat_id = chat.get("id")
        if not chat_id:
            continue

        messages = await graph.get_chat_messages(settings.gvp_email, chat_id)
        for msg in messages:
            teams_message_id = msg.get("id")
            if teams_message_id:
                existing = await db.execute(
                    select(TeamsMessage).where(TeamsMessage.teams_message_id == teams_message_id)
                )
                if existing.scalars().first():
                    continue

            content = (msg.get("body") or {}).get("content", "")
            if not content:
                continue

            sender = (msg.get("from") or {}).get("user") or {}
            received_at_raw = msg.get("createdDateTime")
            try:
                received_at = date_parser.parse(received_at_raw) if received_at_raw else datetime.now(timezone.utc)
            except (ValueError, OverflowError):
                received_at = datetime.now(timezone.utc)

            record = TeamsMessage(
                teams_message_id=teams_message_id,
                source="CHAT",
                chat_id=chat_id,
                sender_name=sender.get("displayName"),
                sender_id=sender.get("id"),
                content=content,
                received_at=received_at,
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)

            await _analyze_and_auto_create(record, db)
            count += 1

    logger.info(f"Persisted {count} new Teams message(s)")
    return count


async def _analyze_and_auto_create(message, db) -> None:
    """AI-extract meeting requests / action items / decisions / commitments /
    risks / reschedules from a Teams message and automatically update the
    schedule, task register, decision register, etc. — same pipeline as
    app/services/whatsapp.py and app/services/email_processor.py."""
    try:
        from agents.email_agent import EmailIntelligenceAgent
        from app.integrations.openai_client import get_openai_client

        agent = EmailIntelligenceAgent(get_openai_client())
        analysis = await agent.analyze_email(
            subject="Microsoft Teams message",
            body=message.content,
            sender=message.sender_name or message.sender_id or "",
            received_at=message.received_at.isoformat(),
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
        logger.warning(f"Teams AI analysis failed: {e}")
        return

    message.processed = True
    await db.commit()

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
    await auto_create_records("TEAMS", str(message.id), extracted, owner_id, db)
    await apply_reschedules(message.ai_reschedule_requests, owner_id, db)


async def get_teams_stats(db: AsyncSession) -> dict:
    from app.models.teams_message import TeamsMessage

    result = await db.execute(select(TeamsMessage))
    messages = result.scalars().all()
    return {
        "total": len(messages),
        "processed": sum(1 for m in messages if m.processed),
        "with_meeting_requests": sum(1 for m in messages if m.ai_meeting_requests),
        "with_action_items": sum(1 for m in messages if m.ai_action_items),
    }
