"""
Auth-related Pydantic schemas.
"""
from uuid import UUID

from pydantic import BaseModel

from app.models.user import UserRole


class Token(BaseModel):
    access_token:  str
    refresh_token: str | None = None
    token_type:    str = "bearer"
    expires_in:    int = 3600  # seconds


class TokenData(BaseModel):
    user_id: UUID
    email:   str
    role:    UserRole


class LoginRequest(BaseModel):
    """Credentials for local dev login."""
    # Plain str, not EmailStr — see app/schemas/user.py for why (.local seed accounts).
    email:    str
    password: str


# Alias kept for backward compat
LoginData = LoginRequest


class MicrosoftAuthRequest(BaseModel):
    """Microsoft OAuth2 authorisation code exchange."""
    code:         str
    redirect_uri: str | None = "http://localhost:3000/auth/callback"


class ProfileUpdate(BaseModel):
    full_name:   str | None = None
    avatar_url:  str | None = None
    phone:       str | None = None
    preferences: dict | None = None


class MFAChallenge(BaseModel):
    """Returned by /login instead of a Token when the account has MFA enabled."""
    mfa_required:   bool = True
    challenge_token: str


class MFASetupResponse(BaseModel):
    secret:          str
    otpauth_uri:     str
    qr_code_base64:  str | None = None


class MFAEnableRequest(BaseModel):
    code: str


class MFAEnableResponse(BaseModel):
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    challenge_token: str
    code:            str


class MFADisableRequest(BaseModel):
    password: str
