import logging
from datetime import datetime, timedelta
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.calendar import Event
from app.models.event import EventStatus, EventType
from app.models.user import User
from app.schemas.calendar import EventCreate, EventResponse, EventUpdate
from app.services.calendar import check_conflicts, sync_outlook_calendar
from app.services.calendar_service import CalendarService

router = APIRouter()
logger = logging.getLogger(__name__)


def _to_graph_payload(event: Event) -> dict:
    return {
        "subject": event.title,
        "start": {"dateTime": event.start_datetime.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": event.end_datetime.isoformat(), "timeZone": "UTC"},
        "location": {"displayName": event.location or ""},
    }

@router.get("/events", response_model=list[EventResponse])
async def list_events(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    event_type: str | None = None,
    priority: str | None = None,
    owner_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List events with optional filters."""
    query = select(Event)
    if date_from:
        query = query.where(Event.start_datetime >= date_from)
    if date_to:
        query = query.where(Event.end_datetime <= date_to)
    if event_type:
        query = query.where(Event.event_type == event_type)
    if priority:
        query = query.where(Event.priority == priority)
    if owner_id:
        query = query.where(Event.owner_id == owner_id)

    query = query.order_by(Event.start_datetime)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/events", response_model=EventResponse)
async def create_event(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new calendar event."""
    new_event = Event(**event_in.model_dump(exclude={'owner_id'}), owner_id=current_user.id)
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    try:
        graph_event = await CalendarService().create_event(_to_graph_payload(new_event), db)
        if getattr(graph_event, "id", None):
            new_event.outlook_event_id = graph_event.id
            await db.commit()
            await db.refresh(new_event)
    except Exception as e:
        logger.warning(f"Failed to push new event to Outlook: {e}")

    return new_event

@router.get("/today", response_model=list[EventResponse])
async def get_today_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Today's events sorted by time."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    query = select(Event).where(
        and_(Event.start_datetime >= today, Event.start_datetime < tomorrow)
    ).order_by(Event.start_datetime)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/tomorrow", response_model=list[EventResponse])
async def get_tomorrow_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Tomorrow's events sorted by time."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)

    query = select(Event).where(
        and_(Event.start_datetime >= tomorrow, Event.start_datetime < day_after)
    ).order_by(Event.start_datetime)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/week", response_model=list[EventResponse])
async def get_week_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """This week's events."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_week = today + timedelta(days=7)
    
    query = select(Event).where(
        and_(Event.start_datetime >= today, Event.start_datetime < next_week)
    ).order_by(Event.start_datetime)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/upcoming-board", response_model=list[EventResponse])
async def get_upcoming_board(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Next 10 board meetings."""
    now = datetime.now()
    query = select(Event).where(
        and_(Event.start_datetime >= now, Event.event_type == EventType.BOARD)
    ).order_by(Event.start_datetime).limit(10)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/sync")
async def sync_calendar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger manual calendar sync from Outlook."""
    await sync_outlook_calendar(db)
    return {"message": "Calendar sync triggered"}

@router.get("/conflicts")
async def get_conflicts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Detect scheduling conflicts."""
    conflicts = await check_conflicts(current_user.id, db)
    return {"conflicts": conflicts}
@router.get("/events/{event_id}/prep", response_model=dict)
async def get_event_prep(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Meeting-prep pack for a calendar event: agenda, attendees, AI talking
    points, and related reference documents (matched by title keyword)."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    agenda_items = [line.strip("-• ").strip() for line in (event.agenda or "").splitlines() if line.strip()]

    from agents.orchestrator import _extract_search_keywords
    from app.services.search import global_search

    documents: list = []
    seen_doc_ids: set = set()
    for keyword in _extract_search_keywords(event.title, max_keywords=3) or [event.title]:
        for hit in await global_search(keyword, "documents", 5, db):
            if hit["id"] not in seen_doc_ids:
                seen_doc_ids.add(hit["id"])
                documents.append(hit)
    documents = documents[:5]

    talking_points: list = []
    try:
        from agents.orchestrator import orchestrator
        talking_points = await orchestrator.calendar_agent.generate_meeting_talking_points(
            event.title,
            {"location": event.location, "preparation_required": event.preparation_required},
            documents,
        )
    except Exception as e:
        logger.warning(f"Failed to generate talking points for event {event_id}: {e}")

    return {
        "event_id": str(event.id),
        "title": event.title,
        "agenda": agenda_items,
        "attendees": event.attendees or [],
        "talking_points": talking_points,
        "documents": documents,
    }

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get event detail."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_in: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    for field, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)

    if event.outlook_event_id:
        try:
            await CalendarService().update_event(event.outlook_event_id, _to_graph_payload(event), db)
        except Exception as e:
            logger.warning(f"Failed to push event update to Outlook: {e}")

    return event

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.outlook_event_id:
        try:
            await CalendarService().delete_event(event.outlook_event_id, db)
        except Exception as e:
            logger.warning(f"Failed to delete event from Outlook: {e}")

    await db.delete(event)
    await db.commit()
    return {"message": "Event deleted successfully"}

@router.post("/events/{event_id}/confirm")
async def confirm_attendance(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Confirm attendance."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.status = EventStatus.CONFIRMED
    await db.commit()
    await db.refresh(event)
    status_value = event.status.value if hasattr(event.status, "value") else str(event.status)
    return {"message": "Attendance confirmed", "status": status_value}

