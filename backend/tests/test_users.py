import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_users(client: AsyncClient):
    response = await client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    import uuid
    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/users/{random_id}")
    assert response.status_code == 404
