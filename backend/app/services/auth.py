"""
Auth service — JWT creation/verification and password hashing.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from app.config import get_settings

settings = get_settings()


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------
def hash_password(plain: str) -> str:
    """Hash a plain-text password."""
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against its hash."""
    if not hashed:
        return False
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# MFA (TOTP) — local login only. SSO users get MFA via Entra Conditional
# Access at the tenant level, not through any of this.
# ---------------------------------------------------------------------------
def generate_totp_secret() -> str:
    import pyotp
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "EOIS") -> str:
    import pyotp
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def get_totp_qr_code_base64(otpauth_uri: str) -> str | None:
    """Renders the provisioning URI as a base64 PNG so the frontend can show
    a scannable QR code without needing its own QR library. Returns None if
    the qrcode package isn't installed — manual secret entry still works."""
    try:
        import base64
        import io

        import qrcode
        img = qrcode.make(otpauth_uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except ImportError:
        return None


def verify_totp_code(secret: str, code: str) -> bool:
    import pyotp
    if not secret or not code:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def generate_backup_codes(count: int = 8) -> list[str]:
    import secrets
    return [secrets.token_hex(4) for _ in range(count)]


def verify_and_consume_backup_code(hashed_codes: list[str], code: str) -> list[str] | None:
    """Checks `code` against the stored (hashed) backup codes. Returns the
    updated list with that code removed on success, or None if it didn't match."""
    for hashed in hashed_codes:
        if verify_password(code, hashed):
            return [h for h in hashed_codes if h != hashed]
    return None


def create_mfa_challenge_token(user_id) -> str:
    """Short-lived token proving the user already passed the password check,
    issued between /login and /mfa/verify — not a full session token."""
    to_encode = {"sub": str(user_id), "type": "mfa_challenge"}
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_mfa_challenge_token(token: str) -> str | None:
    """Returns the user id encoded in a valid, unexpired MFA challenge token, or None."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "mfa_challenge":
        return None
    return payload.get("sub")


# ---------------------------------------------------------------------------
# Microsoft token exchange (stub — fills with real MSAL when credentials set)
# ---------------------------------------------------------------------------
async def exchange_ms_token(code: str, redirect_uri: str | None = None) -> dict | None:
    """Exchange a Microsoft auth code for user info."""
    if not settings.microsoft_graph_enabled:
        # Dev-mode mock: return a fake MS user
        return {
            "email":       "dev-user@dangote.com",
            "name":        "Dev User",
            "microsoft_id": "mock-ms-id-12345",
        }

    try:
        import msal
        app_client = msal.ConfidentialClientApplication(
            settings.azure_client_id,
            authority=settings.azure_authority,
            client_credential=settings.azure_client_secret,
        )
        result = app_client.acquire_token_by_authorization_code(
            code,
            scopes=["User.Read"],
            redirect_uri=redirect_uri or "http://localhost:3000/auth/callback",
        )
        if "access_token" not in result:
            return None

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.ms_graph_endpoint}/me",
                headers={"Authorization": f"Bearer {result['access_token']}"},
            )
            user_data = resp.json()
            return {
                "email":        user_data.get("mail") or user_data.get("userPrincipalName"),
                "name":         user_data.get("displayName"),
                "microsoft_id": user_data.get("id"),
            }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"MS token exchange failed: {e}")
        return None
