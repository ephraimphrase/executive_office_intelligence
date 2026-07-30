"""Compatibility shim — wraps CalendarService for router."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.calendar_service import CalendarService

_svc = CalendarService()

async def sync_outlook_calendar(db: AsyncSession) -> int:
    return await _svc.sync_from_outlook(db)

async def check_conflicts(owner_id, db: AsyncSession) -> list:
    return await _svc.detect_conflicts(owner_id, db)
