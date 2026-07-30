
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User, UserRole

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT and return the authenticated User."""
    if not token:
        token = request.cookies.get("access_token")
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 'sub' may be a user UUID or email depending on how the token was issued.
    # Branching on which (rather than comparing both in one OR'd query) avoids
    # handing a plain string to the UUID column's bind processor, which raises
    # AttributeError: 'str' object has no attribute 'hex' — this used to break
    # every single authenticated request; only test overrides of this
    # dependency kept it from being caught by the test suite.
    import uuid as uuid_lib

    from sqlalchemy.future import select as sa_select

    try:
        subject_uuid = uuid_lib.UUID(subject)
    except ValueError:
        subject_uuid = None

    stmt = sa_select(User).where(User.id == subject_uuid) if subject_uuid is not None \
        else sa_select(User).where(User.email == subject)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def require_gvp_or_cos(current_user: User = Depends(get_current_active_user)) -> User:
    allowed_roles = [UserRole.ADMIN, UserRole.GVP, UserRole.CHIEF_OF_STAFF]
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def require_staff(current_user: User = Depends(get_current_active_user)) -> User:
    staff_roles = [
        UserRole.ADMIN, UserRole.GVP, UserRole.CHIEF_OF_STAFF, 
        UserRole.EXECUTIVE_ASSISTANT, UserRole.PERSONAL_ASSISTANT,
        UserRole.DEPARTMENT_HEAD, UserRole.BOARD_SECRETARIAT
    ]
    if current_user.role not in staff_roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def get_pagination(skip: int = 0, limit: int = 50) -> dict:
    return {"skip": skip, "limit": limit}
