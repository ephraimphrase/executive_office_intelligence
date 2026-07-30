import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_notifications(client: AsyncClient):
    response = await client.get("/api/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_notifications_unread_count(client: AsyncClient):
    response = await client.get("/api/notifications/unread-count")
    assert response.status_code == 200
    assert "unread_count" in response.json()
