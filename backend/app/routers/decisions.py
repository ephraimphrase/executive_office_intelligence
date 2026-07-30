from datetime import datetime
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.decision import Decision, DecisionStatus
from app.models.user import User
from app.services.audit import log_action
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
)

router = APIRouter()

@router.get("", response_model=list[DecisionResponse])
async def list_decisions(
    status: str | None = None,
    department: str | None = None,
    made_by: UUID | None = None,
    date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List decisions with optional filters."""
    query = select(Decision)
    if status:
        query = query.where(Decision.status == status)
    if department:
        query = query.where(Decision.department == department)
    if made_by:
        query = query.where(Decision.made_by_user_id == made_by)
    if date:
        query = query.where(Decision.decision_date >= date)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=DecisionResponse)
async def create_decision(
    decision_in: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create decision."""
    data = decision_in.model_dump(exclude_unset=True)
    if "made_by_user_id" not in data or not data["made_by_user_id"]:
        data["made_by_user_id"] = current_user.id
    new_decision = Decision(**data)
    db.add(new_decision)
    await db.commit()
    await db.refresh(new_decision)
    await log_action(db, current_user, "DECISION_CREATE", "Decision", new_decision.id,
                      {"description": new_decision.description[:200]})
    return new_decision

@router.get("/pending", response_model=list[DecisionResponse])
async def get_pending_decisions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Decisions pending implementation."""
    query = select(Decision).where(Decision.status == DecisionStatus.PENDING_IMPLEMENTATION)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/stats", response_model=dict)
async def get_decision_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Decision statistics."""
    result = await db.execute(select(Decision))
    decisions = result.scalars().all()

    by_department: dict = {}
    implemented = 0
    pending = 0
    for d in decisions:
        dept = d.department or "General"
        by_department[dept] = by_department.get(dept, 0) + 1
        if d.status == DecisionStatus.IMPLEMENTED:
            implemented += 1
        elif d.status == DecisionStatus.PENDING_IMPLEMENTATION:
            pending += 1

    return {
        "total": len(decisions),
        "implemented": implemented,
        "pending": pending,
        "by_department": by_department,
    }

@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get decision detail."""
    decision = await db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision

@router.put("/{decision_id}", response_model=DecisionResponse)
async def update_decision(
    decision_id: UUID,
    decision_in: DecisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update decision."""
    decision = await db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    for field, value in decision_in.model_dump(exclude_unset=True).items():
        setattr(decision, field, value)
        
    await db.commit()
    await db.refresh(decision)
    return decision

@router.delete("/{decision_id}")
async def delete_decision(
    decision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete decision."""
    decision = await db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    await db.delete(decision)
    await db.commit()
    await log_action(db, current_user, "DECISION_DELETE", "Decision", decision_id,
                      {"description": decision.description[:200]})
    return {"message": "Decision deleted successfully"}

@router.put("/{decision_id}/status", response_model=DecisionResponse)
async def update_decision_status(
    decision_id: UUID,
    status_update: DecisionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update implementation status."""
    decision = await db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    old_status = str(decision.status)
    decision.status = status_update.status
    await db.commit()
    await db.refresh(decision)
    await log_action(db, current_user, "DECISION_STATUS_CHANGE", "Decision", decision.id,
                      {"old_status": old_status, "new_status": str(decision.status)})
    return decision


