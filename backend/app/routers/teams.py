from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.teams_message import TeamsMessage
from app.models.user import User
from app.schemas.teams import TeamsMessageResponse
from app.services.teams import get_teams_stats, sync_teams_messages

router = APIRouter()

@router.post("/sync")
async def sync_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger a manual Teams chat sync."""
    count = await sync_teams_messages(db)
    return {"message": "Teams sync triggered", "new_message_count": count}

@router.get("/messages", response_model=list[TeamsMessageResponse])
async def list_messages(
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List processed Teams messages."""
    query = select(TeamsMessage).order_by(TeamsMessage.received_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/messages/{message_id}", response_model=TeamsMessageResponse)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get message detail."""
    message = await db.get(TeamsMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/stats")
async def teams_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Teams integration statistics."""
    return await get_teams_stats(db)
