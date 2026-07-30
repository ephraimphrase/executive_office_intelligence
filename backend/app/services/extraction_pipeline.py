"""Shared AI-extraction-to-database pipeline used by email, WhatsApp, and
Teams ingestion. Turns extracted meeting requests / action items / decisions
/ commitments / risks into real rows automatically — the spec's requirement
that these be captured "without requiring manual data entry" across every
communication channel, not just email."""
import logging

logger = logging.getLogger(__name__)


def _parse_date(raw):
    if not raw:
        return None
    try:
        from dateutil import parser as date_parser
        return date_parser.parse(raw)
    except (ValueError, OverflowError, TypeError):
        return None


async def auto_create_records(source_type: str, source_id: str, extracted: dict, owner_id, db) -> dict:
    """Create Event/Task/Decision/Commitment/Risk rows from AI-extracted data.
    Returns the created objects grouped by type (e.g. so callers can notify
    on newly created high-severity risks)."""
    created: dict = {"events": [], "tasks": [], "decisions": [], "commitments": [], "risks": []}
    if owner_id is None or db is None:
        return created

    from app.services.calendar_service import CalendarService
    from app.services.task_service import TaskService

    cal_svc = CalendarService()
    for meeting in (extracted.get("meeting_requests") or []):
        event = await cal_svc.create_from_extraction(meeting, source_id, owner_id, db, source_type=source_type)
        created["events"].append(event)

    task_svc = TaskService()
    for action_item in (extracted.get("action_items") or []):
        task = await task_svc.create_from_action_item(action_item, source_type, source_id, owner_id, db)
        created["tasks"].append(task)

    department = extracted.get("department")

    from app.models.decision import Decision, DecisionStatus
    for decision in (extracted.get("decisions") or []):
        row = Decision(
            description=(decision.get("description") or "Untitled decision")[:2000],
            context=decision.get("context"),
            made_by=decision.get("made_by"),
            department=department,
            status=DecisionStatus.PENDING_IMPLEMENTATION,
            source_type=source_type,
            source_id=source_id,
            ai_extracted=True,
        )
        db.add(row)
        created["decisions"].append(row)

    from app.models.commitment import Commitment
    for commitment in (extracted.get("commitments") or []):
        row = Commitment(
            description=(commitment.get("description") or "Untitled commitment")[:2000],
            owner=commitment.get("by_whom"),
            made_by=commitment.get("by_whom"),
            deadline=_parse_date(commitment.get("deadline")),
            department=department,
            context=commitment.get("context"),
            source_type=source_type,
            source_id=source_id,
            ai_extracted=True,
        )
        db.add(row)
        created["commitments"].append(row)

    from app.models.risk import Risk, RiskSeverity
    valid_severities = {s.value for s in RiskSeverity}
    for risk in (extracted.get("risks") or []):
        severity = (risk.get("severity") or "MEDIUM").upper()
        if severity not in valid_severities:
            severity = "MEDIUM"
        row = Risk(
            description=(risk.get("description") or "Untitled risk")[:2000],
            category=risk.get("category"),
            severity=severity,
            department=department,
            source_type=source_type,
            source_id=source_id,
            ai_extracted=True,
        )
        db.add(row)
        created["risks"].append(row)

    await db.commit()
    for group in created.values():
        for obj in group:
            if obj is not None:
                await db.refresh(obj)

    await _notify_new_risks(created["risks"], owner_id, db)
    return created


async def _notify_new_risks(risks: list, owner_id, db) -> None:
    """Fire a RISK_ALERT notification for any newly auto-created CRITICAL/HIGH risk."""
    if not risks:
        return

    from app.models.notification import NotificationPriority, NotificationType
    from app.models.risk import RiskSeverity
    from app.services.notification_service import NotificationService

    notif_svc = NotificationService()
    for risk in risks:
        if risk.severity not in (RiskSeverity.CRITICAL, RiskSeverity.HIGH):
            continue
        await notif_svc.create_notification(
            user_id=owner_id,
            type=NotificationType.RISK_ALERT,
            title=f"New {risk.severity.value} risk identified",
            message=risk.description[:200],
            priority=NotificationPriority.URGENT if risk.severity == RiskSeverity.CRITICAL else NotificationPriority.HIGH,
            reference_type="RISK",
            reference_id=risk.id,
            db=db,
        )


async def apply_reschedules(reschedule_requests: list, owner_id, db) -> None:
    """Apply any 'move it to Wednesday' / 'postpone till Friday'-style requests."""
    if owner_id is None or db is None:
        return

    from app.services.calendar_service import CalendarService
    cal_svc = CalendarService()
    for reschedule in (reschedule_requests or []):
        await cal_svc.apply_reschedule(reschedule, owner_id, db)
