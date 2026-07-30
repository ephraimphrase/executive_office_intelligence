from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.risk import Risk, RiskStatus
from app.models.user import User
from app.schemas.risk import RiskCreate, RiskResponse, RiskUpdate
from app.services.audit import log_action

router = APIRouter()

@router.get("", response_model=list[RiskResponse])
async def list_risks(
    status: str | None = None,
    severity: str | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List risks with optional filters (the Risk Register)."""
    query = select(Risk)
    if status:
        query = query.where(Risk.status == status)
    if severity:
        query = query.where(Risk.severity == severity)
    if department:
        query = query.where(Risk.department == department)

    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=RiskResponse)
async def create_risk(
    risk_in: RiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create risk."""
    data = risk_in.model_dump(exclude_unset=True)
    if not data.get("owner_user_id"):
        data["owner_user_id"] = current_user.id
    new_risk = Risk(**data)
    db.add(new_risk)
    await db.commit()
    await db.refresh(new_risk)
    return new_risk

@router.get("/open", response_model=list[RiskResponse])
async def get_open_risks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Open (unmitigated) risks."""
    query = select(Risk).where(Risk.status == RiskStatus.OPEN)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get risk detail."""
    risk = await db.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk

@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: UUID,
    risk_in: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update risk."""
    risk = await db.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    for field, value in risk_in.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)

    await db.commit()
    await db.refresh(risk)
    return risk

@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete risk."""
    risk = await db.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    await db.delete(risk)
    await db.commit()
    await log_action(db, current_user, "RISK_DELETE", "Risk", risk_id, {"description": risk.description[:200]})
    return {"message": "Risk deleted successfully"}
