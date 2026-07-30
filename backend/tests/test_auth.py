import pytest
from httpx import AsyncClient
from app.services.auth import hash_password, verify_password

def test_password_hashing():
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]
