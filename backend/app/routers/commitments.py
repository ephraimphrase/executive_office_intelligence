from datetime import datetime, timedelta
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.commitment import Commitment, CommitmentStatus
from app.models.user import User
from app.services.audit import log_action
from app.schemas.commitment import (
    CommitmentCreate,
    CommitmentResponse,
    CommitmentStatusUpdate,
    CommitmentUpdate,
)

router = APIRouter()

@router.get("", response_model=list[CommitmentResponse])
async def list_commitments(
    status: str | None = None,
    owner_id: UUID | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List commitments with filters."""
    query = select(Commitment)
    if status:
        query = query.where(Commitment.status == status)
    if owner_id:
        query = query.where(Commitment.owner_id == owner_id)
    if department:
        query = query.where(Commitment.department == department)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=CommitmentResponse)
async def create_commitment(
    commitment_in: CommitmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create commitment."""
    new_commitment = Commitment(**commitment_in.model_dump(exclude={'owner_user_id'}), owner_user_id=current_user.id)
    if not new_commitment.owner_user_id:
        new_commitment.owner_user_id = current_user.id
    db.add(new_commitment)
    await db.commit()
    await db.refresh(new_commitment)
    return new_commitment

@router.get("/overdue", response_model=list[CommitmentResponse])
async def get_overdue_commitments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Overdue commitments."""
    now = datetime.now()
    query = select(Commitment).where(
        and_(Commitment.deadline < now, Commitment.status != CommitmentStatus.FULFILLED)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/due-soon", response_model=list[CommitmentResponse])
async def get_due_soon_commitments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Commitments due in next 7 days."""
    now = datetime.now()
    next_week = now + timedelta(days=7)
    query = select(Commitment).where(
        and_(
            Commitment.deadline >= now, 
            Commitment.deadline <= next_week,
            Commitment.status != CommitmentStatus.FULFILLED
        )
    )
    result = await db.execute(query)
    return result.scalars().all()
@router.get("/{commitment_id}", response_model=CommitmentResponse)
async def get_commitment(
    commitment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get detail."""
    commitment = await db.get(Commitment, commitment_id)
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
    return commitment

@router.put("/{commitment_id}", response_model=CommitmentResponse)
async def update_commitment(
    commitment_id: UUID,
    commitment_in: CommitmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update."""
    commitment = await db.get(Commitment, commitment_id)
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
        
    for field, value in commitment_in.model_dump(exclude_unset=True).items():
        setattr(commitment, field, value)
        
    await db.commit()
    await db.refresh(commitment)
    return commitment

@router.delete("/{commitment_id}")
async def delete_commitment(
    commitment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete."""
    commitment = await db.get(Commitment, commitment_id)
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
        
    await db.delete(commitment)
    await db.commit()
    await log_action(db, current_user, "COMMITMENT_DELETE", "Commitment", commitment_id,
                      {"description": commitment.description[:200]})
    return {"message": "Commitment deleted successfully"}

@router.put("/{commitment_id}/status", response_model=CommitmentResponse)
async def update_commitment_status(
    commitment_id: UUID,
    status_update: CommitmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update status."""
    commitment = await db.get(Commitment, commitment_id)
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
        
    commitment.status = status_update.status
    await db.commit()
    await db.refresh(commitment)
    return commitment

