"""Compatibility shim — wraps BriefingGeneratorService for router."""
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.briefing_generator import BriefingGeneratorService

_svc = BriefingGeneratorService()

async def generate_daily_briefing(target_date: date, db: AsyncSession):
    return await _svc.generate_briefing(target_date, db)

def build_briefing_record(pack, target_date: date):
    """Map a BriefingPack onto every field of the Briefing model — the
    router used to only fill events_summary/tasks_summary/full_content and
    silently drop everything else (weather, critical emails, risks, pending
    decisions, travel, talking points)."""
    from app.models.briefing import Briefing

    emails = getattr(pack, "emails", []) or []
    return Briefing(
        date=target_date,
        events_summary={"events": getattr(pack, "events", [])},
        tasks_summary={"tasks": getattr(pack, "tasks", [])},
        email_highlights={"emails": emails},
        pending_decisions={"decisions": getattr(pack, "decisions", [])},
        travel_info={"travel": getattr(pack, "travel", [])},
        weather_info=getattr(pack, "weather", None) or {},
        risks_summary={"risks": getattr(pack, "risks", []), "summary": getattr(pack, "risk_summary", "")},
        talking_points=getattr(pack, "talking_points", []),
        suggested_priorities=getattr(pack, "priorities", []),
        critical_alerts=[e.get("subject", "") for e in emails[:5]],
        full_content={"narrative": getattr(pack, "narrative", "")},
    )

async def export_briefing_doc(briefing, fmt: str = 'docx', db: AsyncSession = None) -> bytes:
    if fmt == 'pdf':
        return await _svc.export_to_pdf(briefing, db)
    if fmt == 'pptx':
        return await _svc.export_to_pptx(briefing, db)
    return await _svc.export_to_docx(briefing, db)

async def send_briefing_email(briefing, recipients: list) -> bool:
    return await _svc.send_briefing_email(briefing, recipients)
