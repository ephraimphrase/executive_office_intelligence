from datetime import datetime
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.email import Email
from app.models.email_record import EmailPriority, EmailStatus
from app.models.user import User
from app.schemas.email import EmailResponse, EmailStatusUpdate
from app.services.email import (
    create_event_from_email,
    create_task_from_email,
    process_unprocessed_emails,
    sync_outlook_emails,
)

router = APIRouter()

@router.get("", response_model=list[EmailResponse])
async def list_emails(
    priority: str | None = None,
    status: str | None = None,
    department: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List emails with optional filters."""
    query = select(Email)
    if priority:
        query = query.where(Email.priority == priority)
    if status:
        query = query.where(Email.status == status)
    if department:
        query = query.where(Email.department == department)
    if date_from:
        query = query.where(Email.received_at >= date_from)
    if date_to:
        query = query.where(Email.received_at <= date_to)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/process")
async def process_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger AI processing on all unprocessed emails."""
    count = await process_unprocessed_emails(db)
    return {"message": "Email AI processing completed", "processed_count": count}

@router.get("/critical", response_model=list[EmailResponse])
async def get_critical_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get critical unread emails."""
    query = select(Email).where(
        and_(
            Email.priority == EmailPriority.URGENT,
            Email.status == EmailStatus.UNREAD
        )
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/stats")
async def email_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Email statistics."""
    result = await db.execute(select(Email))
    emails = result.scalars().all()
    total = len(emails)
    critical_count = sum(1 for e in emails if e.priority == EmailPriority.URGENT)
    high_count = sum(1 for e in emails if e.priority == EmailPriority.HIGH)
    unread_count = sum(1 for e in emails if e.status == EmailStatus.UNREAD)
    replied_count = sum(1 for e in emails if e.status == EmailStatus.REPLIED)
    response_rate = f"{round((replied_count / total) * 100)}%" if total else "0%"
    return {
        "total_count": total,
        "critical_count": critical_count,
        "high_count": high_count,
        "unread_count": unread_count,
        "response_rate": response_rate,
    }

@router.post("/sync")
async def sync_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger manual email sync from Outlook."""
    count = await sync_outlook_emails(db)
    return {"message": "Email sync triggered", "new_email_count": count}

@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get email detail with AI analysis."""
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.put("/{email_id}/status", response_model=EmailResponse)
async def update_email_status(
    email_id: UUID,
    status_update: EmailStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mark read/archived/etc."""
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    email.status = status_update.status
    await db.commit()
    await db.refresh(email)
    return email

@router.post("/{email_id}/create-task")
async def create_task_from_email_endpoint(
    email_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create task from the first AI-extracted action item on this email."""
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    action_items = email.ai_action_items or []
    action_item = action_items[0] if action_items else {
        "description": email.subject or "Follow up on email",
        "department": email.department_category,
    }
    task = await create_task_from_email(email, action_item, current_user.id, db)
    return {"message": "Task created successfully", "task_id": str(task.id)}

@router.post("/{email_id}/create-event")
async def create_event_from_email_endpoint(
    email_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create calendar event from the first AI-extracted meeting request on this email."""
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    meeting_requests = email.ai_meeting_requests or []
    meeting_data = meeting_requests[0] if meeting_requests else {"title": email.subject or "Meeting"}
    event = await create_event_from_email(email, meeting_data, current_user.id, db)
    return {"message": "Event created successfully", "event_id": str(event.id)}



@router.get("/thread/{thread_id}", response_model=list[EmailResponse])
async def get_email_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get email thread."""
    query = select(Email).where(
        Email.thread_id == thread_id
    ).order_by(Email.received_at)
    result = await db.execute(query)
    return result.scalars().all()
