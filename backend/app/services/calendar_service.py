import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.integrations.microsoft_graph import MicrosoftGraphClient
from app.models.event import Event, EventSourceType

logger = logging.getLogger(__name__)


async def get_gvp_owner_id(db):
    """Resolve the User row representing the GVP mailbox owner, if seeded."""
    if db is None:
        return None
    from app.config import get_settings
    from app.models.user import User

    settings = get_settings()
    result = await db.execute(select(User).where(User.email == settings.gvp_email))
    user = result.scalars().first()
    return user.id if user else None


class CalendarEvent:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class CalendarService:
    def __init__(self):
        self.graph_client = MicrosoftGraphClient()

    async def create_event(self, event_data: dict, db) -> CalendarEvent:
        from app.config import get_settings
        res = await self.graph_client.create_calendar_event(get_settings().gvp_email, event_data)
        return CalendarEvent(**res)

    async def update_event(self, event_id: str, event_data: dict, db) -> CalendarEvent:
        from app.config import get_settings
        res = await self.graph_client.update_calendar_event(get_settings().gvp_email, event_id, event_data)
        return CalendarEvent(**res)

    async def delete_event(self, event_id: str, db) -> bool:
        from app.config import get_settings
        return await self.graph_client.delete_calendar_event(get_settings().gvp_email, event_id)

    async def get_events(self, db, date_from: str, date_to: str, filters: dict) -> list:
        from app.config import get_settings
        events = await self.graph_client.get_calendar_events(get_settings().gvp_email, date_from, date_to)
        return [CalendarEvent(**e) for e in events]

    async def detect_conflicts(self, owner_id, db) -> list:
        """Find pairs of events for `owner_id` whose time ranges overlap."""
        if db is None:
            return []
        result = await db.execute(
            select(Event).where(Event.owner_id == owner_id).order_by(Event.start_datetime)
        )
        events = result.scalars().all()
        conflicts = []
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                a, b = events[i], events[j]
                if a.start_datetime < b.end_datetime and b.start_datetime < a.end_datetime:
                    conflicts.append({
                        "event_a": {"id": str(a.id), "title": a.title,
                                    "start": a.start_datetime.isoformat(), "end": a.end_datetime.isoformat()},
                        "event_b": {"id": str(b.id), "title": b.title,
                                    "start": b.start_datetime.isoformat(), "end": b.end_datetime.isoformat()},
                    })
        return conflicts

    async def sync_from_outlook(self, db) -> int:
        """Pull upcoming Outlook events and persist any not already tracked locally."""
        logger.info("Syncing calendar from outlook...")
        if db is None:
            return 0

        from dateutil import parser as date_parser

        from app.config import get_settings

        owner_id = await get_gvp_owner_id(db)
        if owner_id is None:
            logger.warning("No GVP user found; skipping calendar sync persistence.")
            return 0

        now = datetime.now(timezone.utc)
        window_end = now + timedelta(days=30)
        events_data = await self.graph_client.get_calendar_events(
            get_settings().gvp_email, now.isoformat(), window_end.isoformat()
        )

        count = 0
        for e in events_data:
            outlook_id = e.get("id")
            if outlook_id:
                existing = await db.execute(select(Event).where(Event.outlook_event_id == outlook_id))
                if existing.scalars().first():
                    continue

            start_raw = (e.get("start") or {}).get("dateTime")
            end_raw = (e.get("end") or {}).get("dateTime")
            try:
                start_dt = date_parser.parse(start_raw) if start_raw else now
                end_dt = date_parser.parse(end_raw) if end_raw else start_dt + timedelta(hours=1)
            except (ValueError, OverflowError):
                continue

            event = Event(
                title=e.get("subject") or "Untitled Event",
                start_datetime=start_dt,
                end_datetime=end_dt,
                location=(e.get("location") or {}).get("displayName"),
                owner_id=owner_id,
                source_type=EventSourceType.CALENDAR,
                outlook_event_id=outlook_id,
            )
            db.add(event)
            count += 1

        await db.commit()
        logger.info(f"Persisted {count} new event(s) from Outlook")
        return count

    async def get_today_schedule(self, owner_id, db) -> list:
        """Return today's events for `owner_id`, ordered by start time."""
        if db is None:
            return []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        result = await db.execute(
            select(Event).where(
                Event.owner_id == owner_id,
                Event.start_datetime >= today,
                Event.start_datetime < tomorrow,
            ).order_by(Event.start_datetime)
        )
        return result.scalars().all()

    async def apply_reschedule(self, reschedule_request: dict, owner_id, db) -> Event | None:
        """Find an upcoming event matching `meeting_reference` and move it to the new date/time.

        This is what powers "move the meeting to Wednesday" / "postpone the inspection till Friday" —
        the schedule updates automatically without anyone editing the calendar by hand.
        """
        if db is None or owner_id is None:
            return None

        reference = (reschedule_request.get("meeting_reference") or "").strip()
        if not reference:
            return None

        now = datetime.now()  # naive — Event.start_datetime is stored without tzinfo
        result = await db.execute(
            select(Event).where(Event.owner_id == owner_id, Event.start_datetime >= now)
            .order_by(Event.start_datetime)
        )
        candidates = result.scalars().all()
        if not candidates:
            return None

        reference_lower = reference.lower()
        match = next(
            (e for e in candidates if reference_lower in e.title.lower() or e.title.lower() in reference_lower),
            None,
        )
        if not match:
            return None

        new_date = reschedule_request.get("new_date")
        if not new_date:
            return None

        from dateutil import parser as date_parser

        try:
            new_time = reschedule_request.get("new_time") or match.start_datetime.strftime("%H:%M")
            new_start = date_parser.parse(f"{new_date} {new_time}")
        except (ValueError, OverflowError):
            return None

        duration = match.end_datetime - match.start_datetime
        match.start_datetime = new_start
        match.end_datetime = new_start + duration
        reason = reschedule_request.get("reason")
        note = f"Rescheduled via automated request{f': {reason}' if reason else ''}."
        match.notes = f"{match.notes}\n{note}".strip() if match.notes else note

        await db.commit()
        await db.refresh(match)
        logger.info(f"Rescheduled event {match.id} ('{match.title}') to {new_start.isoformat()}")

        if match.outlook_event_id:
            try:
                await self.update_event(match.outlook_event_id, {
                    "subject": match.title,
                    "start": {"dateTime": match.start_datetime.isoformat(), "timeZone": "UTC"},
                    "end": {"dateTime": match.end_datetime.isoformat(), "timeZone": "UTC"},
                    "location": {"displayName": match.location or ""},
                }, db)
            except Exception as e:
                logger.warning(f"Failed to push reschedule to Outlook: {e}")

        return match

    async def create_from_extraction(self, extracted_meeting: dict, source_id: str, owner_id, db,
                                      source_type: str = "EMAIL") -> Event:
        """Persist a real Event row from an AI-extracted meeting request."""
        from dateutil import parser as date_parser

        title = extracted_meeting.get("title") or "Meeting"
        start = None
        proposed_date = extracted_meeting.get("proposed_date")
        if proposed_date:
            try:
                combined = f"{proposed_date} {extracted_meeting.get('proposed_time') or '09:00'}"
                start = date_parser.parse(combined)
            except (ValueError, OverflowError):
                start = None
        if start is None:
            start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)

        confidence = extracted_meeting.get("confidence_score")
        try:
            confidence = float(confidence) if confidence is not None else None
        except (TypeError, ValueError):
            confidence = None

        event = Event(
            title=title,
            start_datetime=start,
            end_datetime=end,
            location=extracted_meeting.get("location"),
            owner_id=owner_id,
            source_type=EventSourceType[source_type] if source_type in EventSourceType.__members__ else EventSourceType.EMAIL,
            source_id=source_id,
            attendees=extracted_meeting.get("attendees") or [],
            agenda=extracted_meeting.get("agenda"),
            preparation_required=extracted_meeting.get("preparation_required"),
            ai_confidence=confidence,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
