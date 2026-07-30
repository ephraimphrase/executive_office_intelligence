from datetime import date
from uuid import UUID
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.briefing import Briefing
from app.models.user import User
from app.schemas.briefing import BriefingResponse
from app.services.briefing import (
    build_briefing_record,
    export_briefing_doc,
    generate_daily_briefing,
    send_briefing_email,
)

router = APIRouter()

@router.get("/today", response_model=BriefingResponse)
async def get_today_briefing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Today's briefing pack."""
    today = date.today()
    query = select(Briefing).where(Briefing.date == today)
    result = await db.execute(query)
    briefing = result.scalar_one_or_none()
    
    if not briefing:
        # Auto-generate if not exists
        pack = await generate_daily_briefing(today, db)
        briefing = build_briefing_record(pack, today)
        db.add(briefing)
        await db.commit()
        await db.refresh(briefing)

    return briefing

@router.get("/date/{target_date}", response_model=BriefingResponse)
async def get_briefing_by_date(
    target_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Briefing for specific date (YYYY-MM-DD)."""
    query = select(Briefing).where(Briefing.date == target_date)
    result = await db.execute(query)
    briefing = result.scalar_one_or_none()
    
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found for this date")
        
    return briefing

@router.get("", response_model=list[BriefingResponse])
async def list_briefings(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List past briefings."""
    query = select(Briefing).order_by(Briefing.date.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/generate", response_model=BriefingResponse)
async def generate_briefing(
    target_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Manually trigger briefing generation for a date."""
    pack = await generate_daily_briefing(target_date, db)
    briefing = build_briefing_record(pack, target_date)
    db.add(briefing)
    await db.commit()
    await db.refresh(briefing)
    return briefing

@router.get("/{briefing_id}/export")
async def export_briefing(
    briefing_id: UUID,
    format: str = Query("pdf", pattern="^(pdf|docx|pptx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Export to DOCX, PDF, or PPTX (slide deck)."""
    briefing = await db.get(Briefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    file_bytes = await export_briefing_doc(briefing, format, db)
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    return Response(
        content=file_bytes,
        media_type=media_types[format],
        headers={"Content-Disposition": f'attachment; filename="Briefing_{briefing.date}.{format}"'},
    )

@router.post("/{briefing_id}/send")
async def send_briefing(
    briefing_id: UUID,
    recipients: list[str],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Email briefing to specified recipients."""
    briefing = await db.get(Briefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
        
    background_tasks.add_task(send_briefing_email, briefing, recipients)
    return {"message": f"Briefing scheduled to be sent to {len(recipients)} recipients"}
