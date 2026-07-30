from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.dependencies import require_admin as get_current_admin_user
from app.models.user import User
from app.schemas.user import RoleUpdate, UserCreate, UserResponse, UserUpdate
from app.services.audit import log_action

router = APIRouter()

@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """List all users, paginated (admin only)."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Create user (admin only)."""
    existing_user = await db.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(**user_in.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await log_action(db, current_user, "USER_CREATE", "User", new_user.id, {"email": new_user.email, "role": str(new_user.role)})
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Get user (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Update user (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    changes = user_in.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    await log_action(db, current_user, "USER_UPDATE", "User", user.id, {"fields": list(changes.keys())})
    return user

@router.delete("/{user_id}")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Deactivate user (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    await db.commit()
    await log_action(db, current_user, "USER_DEACTIVATE", "User", user.id, {"email": user.email})
    return {"message": "User deactivated successfully"}

@router.put("/{user_id}/role", response_model=UserResponse)
async def change_role(
    user_id: UUID,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Change role (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = str(user.role)
    user.role = role_in.role
    await db.commit()
    await db.refresh(user)
    await log_action(db, current_user, "USER_ROLE_CHANGE", "User", user.id,
                      {"email": user.email, "old_role": old_role, "new_role": str(user.role)})
    return user
