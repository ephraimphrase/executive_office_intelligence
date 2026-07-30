from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    # Plain str, not EmailStr: strict RFC validation rejects reserved/
    # special-use TLDs like .local, which this project's own seeded dev
    # admin account (admin@eois.local) uses. The DB doesn't enforce email
    # format either, so there's no real validation being lost.
    email: str
    full_name: str
    role: UserRole = UserRole.READ_ONLY
    avatar_url: str | None = None
    is_active: bool = True
    microsoft_id: str | None = None
    department: str | None = None
    phone: str | None = None
    preferences: dict[str, Any] = {}

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    department: str | None = None
    phone: str | None = None
    preferences: dict[str, Any] | None = None

class RoleUpdate(BaseModel):
    role: UserRole

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

class UserList(BaseModel):
    items: list[UserResponse]
    total: int
    skip: int
    limit: int
