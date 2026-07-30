"""
Auth router — login, refresh, logout, profile.
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import get_settings
from app.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    MFAChallenge,
    MFADisableRequest,
    MFAEnableRequest,
    MFAEnableResponse,
    MFASetupResponse,
    MFAVerifyRequest,
    MicrosoftAuthRequest,
    Token,
)
from app.schemas.user import UserResponse
from app.services.audit import log_action
from app.services.auth import (
    create_access_token,
    create_mfa_challenge_token,
    create_refresh_token,
    decode_mfa_challenge_token,
    exchange_ms_token,
    generate_backup_codes,
    generate_totp_secret,
    get_totp_qr_code_base64,
    get_totp_uri,
    hash_password,
    verify_and_consume_backup_code,
    verify_password,
    verify_totp_code,
)

router = APIRouter()
settings = get_settings()


def _build_token_response(user: User, response: Response) -> dict:
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Set HTTP-only cookies
    # max_age in seconds
    max_age_access = settings.access_token_expire_minutes * 60
    max_age_refresh = 60 * 60 * 24 * 7  # 7 days for refresh token
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=max_age_access,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=max_age_refresh,
    )
    
    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "expires_in":    max_age_access,
    }


@router.post("/login", response_model=Any, summary="Local dev login")
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Authenticate with email + password (development mode).
    In production, use the /microsoft endpoint with Azure SSO.
    Returns a Token, or an MFAChallenge if the account has MFA enabled.
    """
    client_ip = request.client.host if request.client else None
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        await log_action(db, user, "LOGIN_FAILED", "User", getattr(user, "id", None),
                          {"email": credentials.email}, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        await log_action(db, user, "LOGIN_FAILED_INACTIVE", "User", user.id, {}, client_ip)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    if user.mfa_enabled:
        await log_action(db, user, "LOGIN_MFA_CHALLENGE", "User", user.id, {}, client_ip)
        return MFAChallenge(challenge_token=create_mfa_challenge_token(user.id))

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await log_action(db, user, "LOGIN", "User", user.id, {"method": "local"}, client_ip)

    return _build_token_response(user, response)


@router.post("/mfa/verify", response_model=Token, summary="Complete MFA login challenge")
async def mfa_verify(
    payload: MFAVerifyRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Second step of login for MFA-enabled accounts: exchange a challenge
    token + TOTP code (or a backup code) for real session tokens."""
    client_ip = request.client.host if request.client else None
    user_id = decode_mfa_challenge_token(payload.challenge_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA challenge")

    try:
        user = await db.get(User, uuid.UUID(user_id))
    except ValueError:
        user = None
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA challenge")

    if verify_totp_code(user.mfa_secret, payload.code):
        matched = True
    else:
        remaining = verify_and_consume_backup_code(user.mfa_backup_codes or [], payload.code)
        matched = remaining is not None
        if matched:
            user.mfa_backup_codes = remaining
            await log_action(db, user, "MFA_BACKUP_CODE_USED", "User", user.id,
                              {"codes_remaining": len(remaining)}, client_ip)

    if not matched:
        await log_action(db, user, "LOGIN_MFA_FAILED", "User", user.id, {}, client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication code")

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await log_action(db, user, "LOGIN", "User", user.id, {"method": "local+mfa"}, client_ip)

    return _build_token_response(user, response)


@router.post("/mfa/setup", response_model=MFASetupResponse, summary="Begin MFA enrollment")
async def mfa_setup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Generates a new TOTP secret (not yet active — call /mfa/enable with a
    valid code from an authenticator app to turn it on)."""
    secret = generate_totp_secret()
    current_user.mfa_secret = secret
    await db.commit()

    uri = get_totp_uri(secret, current_user.email)
    return MFASetupResponse(secret=secret, otpauth_uri=uri, qr_code_base64=get_totp_qr_code_base64(uri))


@router.post("/mfa/enable", response_model=MFAEnableResponse, summary="Confirm MFA enrollment")
async def mfa_enable(
    payload: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Confirms the code from the authenticator app matches, then turns MFA on
    and returns one-time backup codes (shown once — store them safely)."""
    if not current_user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Call /mfa/setup first")
    if not verify_totp_code(current_user.mfa_secret, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authentication code")

    backup_codes = generate_backup_codes()
    current_user.mfa_enabled = True
    current_user.mfa_backup_codes = [hash_password(c) for c in backup_codes]
    await db.commit()
    await log_action(db, current_user, "MFA_ENABLED", "User", current_user.id)

    return MFAEnableResponse(backup_codes=backup_codes)


@router.post("/mfa/disable", summary="Disable MFA")
async def mfa_disable(
    payload: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Requires the account password again (not just an active session) since
    this lowers the account's security bar."""
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = []
    await db.commit()
    await log_action(db, current_user, "MFA_DISABLED", "User", current_user.id)

    return {"message": "MFA disabled"}


@router.post("/microsoft", response_model=Token, summary="Microsoft SSO login")
async def microsoft_login(
    payload: MicrosoftAuthRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Exchange a Microsoft auth code for EOIS JWT tokens."""
    client_ip = request.client.host if request.client else None
    user_info = await exchange_ms_token(payload.code, payload.redirect_uri)
    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate Microsoft token",
        )

    result = await db.execute(select(User).where(User.email == user_info["email"]))
    user = result.scalars().first()

    if not user:
        # Auto-provision user on first SSO login
        user = User(
            id=uuid.uuid4(),
            email=user_info["email"],
            full_name=user_info.get("name", user_info["email"]),
            microsoft_id=user_info.get("microsoft_id"),
            role=UserRole.READ_ONLY,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await log_action(db, user, "USER_AUTO_PROVISIONED", "User", user.id, {"method": "sso"}, client_ip)

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await log_action(db, user, "LOGIN", "User", user.id, {"method": "sso"}, client_ip)

    return _build_token_response(user, response)


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Issue a new access token for the authenticated user."""
    return _build_token_response(current_user, response)


@router.post("/logout", summary="Logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Clear the authentication cookies."""
    response.delete_cookie("access_token", httponly=True, secure=True, samesite="lax")
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="lax")
    await log_action(db, current_user, "LOGOUT", "User", current_user.id)
    return {"message": "Logged out successfully", "user": current_user.email}


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """Return the currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse, summary="Update profile")
async def update_me(
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update editable profile fields (full_name, avatar_url, preferences)."""
    allowed = {"full_name", "avatar_url", "phone", "preferences"}
    for key, value in update_data.items():
        if key in allowed:
            setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user
