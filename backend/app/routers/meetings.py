from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.meeting import Meeting
from app.models.meeting_record import MeetingType
from app.models.user import User
from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
)
from app.services.meeting import (
    extract_actions_ai,
    extract_decisions_ai,
    generate_agenda_ai,
    generate_minutes_ai,
)

router = APIRouter()

@router.get("", response_model=list[MeetingResponse])
async def list_meetings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List meetings."""
    query = select(Meeting).where(Meeting.created_by_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/committee", response_model=list[MeetingResponse])
async def list_committee_meetings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """The Committee Calendar view — all Board and Executive Committee
    meetings org-wide (not just ones the current user created), ordered by
    date."""
    query = select(Meeting).where(
        Meeting.meeting_type.in_([MeetingType.BOARD, MeetingType.EXECUTIVE_COMMITTEE])
    ).order_by(Meeting.meeting_date)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=MeetingResponse)
async def create_meeting(
    meeting_in: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create meeting record."""
    new_meeting = Meeting(**meeting_in.model_dump(exclude={"created_by_id"}), created_by_id=current_user.id)
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)
    return new_meeting

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get detail."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: UUID,
    meeting_in: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    for field, value in meeting_in.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
        
    await db.commit()
    await db.refresh(meeting)
    return meeting

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    await db.delete(meeting)
    await db.commit()
    return {"message": "Meeting deleted successfully"}

@router.post("/{meeting_id}/generate-agenda")
async def generate_agenda(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """AI generate agenda."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    context = {
        "title": meeting.title,
        "meeting_type": meeting.meeting_type.value if hasattr(meeting.meeting_type, "value") else str(meeting.meeting_type),
        "participants": meeting.participants,
    }
    agenda = await generate_agenda_ai(str(meeting.id), context, db)
    meeting.agenda = agenda
    await db.commit()
    return {"message": "Agenda generated", "agenda": agenda}

@router.post("/{meeting_id}/generate-minutes")
async def generate_minutes(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """AI generate minutes from transcript/notes."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    if not meeting.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required to generate minutes")

    minutes = await generate_minutes_ai(str(meeting.id), meeting.transcript, db)
    meeting.ai_minutes = minutes
    await db.commit()
    return {"message": "Minutes generated", "minutes": minutes}

@router.post("/{meeting_id}/generate-actions")
async def generate_actions(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Extract action items."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    content = meeting.transcript or meeting.minutes or meeting.ai_minutes or ""
    actions = await extract_actions_ai(str(meeting.id), content, db)
    meeting.action_items = actions
    await db.commit()

    from app.services.task_service import TaskService
    task_svc = TaskService()
    created_tasks = []
    for action in actions:
        if isinstance(action, dict):
            task = await task_svc.create_from_action_item(action, "MEETING", str(meeting.id), meeting.created_by_id, db)
            created_tasks.append(str(task.id))

    return {"message": "Actions extracted", "actions": actions, "task_ids": created_tasks}

@router.post("/{meeting_id}/generate-decisions")
async def generate_decisions(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Extract decisions made during the meeting and add them to the Decision Register."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    content = meeting.transcript or meeting.minutes or meeting.ai_minutes or ""
    decisions = await extract_decisions_ai(str(meeting.id), content, db)
    meeting.decision_items = decisions
    await db.commit()

    from app.models.decision import Decision, DecisionStatus
    created_decisions = []
    for decision in decisions:
        if not isinstance(decision, dict):
            continue
        row = Decision(
            description=(decision.get("description") or "Untitled decision")[:2000],
            context=decision.get("context"),
            made_by=decision.get("made_by"),
            made_by_user_id=meeting.created_by_id,
            meeting_id=meeting.id,
            decision_date=meeting.meeting_date,
            status=DecisionStatus.PENDING_IMPLEMENTATION,
            source_type="MEETING",
            source_id=str(meeting.id),
            ai_extracted=True,
        )
        db.add(row)
        created_decisions.append(row)
    await db.commit()

    return {"message": "Decisions extracted", "decisions": decisions, "decision_ids": [str(d.id) for d in created_decisions]}

@router.get("/{meeting_id}/briefing", response_model=dict)
async def get_briefing(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Pre-meeting briefing pack: agenda, participants, and AI talking points."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    from agents.orchestrator import orchestrator
    talking_points = await orchestrator.calendar_agent.generate_meeting_talking_points(
        meeting.title,
        {
            "meeting_type": meeting.meeting_type.value if hasattr(meeting.meeting_type, "value") else str(meeting.meeting_type),
            "chairperson": meeting.chairperson,
        },
        [],
    )

    return {
        "meeting_id": str(meeting.id),
        "title": meeting.title,
        "meeting_date": str(meeting.meeting_date),
        "chairperson": meeting.chairperson,
        "agenda": meeting.agenda or [],
        "participants": meeting.participants or [],
        "board_paper_required": meeting.board_paper_required,
        "talking_points": talking_points,
    }

@router.get("/{meeting_id}/deck")
async def export_meeting_deck(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Export a board-ready PowerPoint deck: agenda, participants, AI talking points."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    from agents.orchestrator import orchestrator
    talking_points = await orchestrator.calendar_agent.generate_meeting_talking_points(
        meeting.title,
        {
            "meeting_type": meeting.meeting_type.value if hasattr(meeting.meeting_type, "value") else str(meeting.meeting_type),
            "chairperson": meeting.chairperson,
        },
        [],
    )

    from app.services.pptx_generator import PowerPointGeneratorService
    pptx_svc = PowerPointGeneratorService()
    file_bytes = await pptx_svc.generate_meeting_deck(
        {
            "title": meeting.title,
            "meeting_date": meeting.meeting_date,
            "agenda": meeting.agenda or [],
            "participants": meeting.participants or [],
            "talking_points": talking_points,
        },
        db,
    )

    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="Meeting_{meeting.meeting_date}_{meeting.title[:30]}.pptx"'},
    )

@router.post("/{meeting_id}/transcript")
async def upload_transcript(
    meeting_id: UUID,
    transcript_text: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload transcript text."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    meeting.transcript = transcript_text
    await db.commit()
    return {"message": "Transcript uploaded"}
