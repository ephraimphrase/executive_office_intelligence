import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_briefings_crud(client: AsyncClient):
    response = await client.get("/api/briefings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_briefings_today(client: AsyncClient):
    response = await client.get("/api/briefings/today")
    assert response.status_code == 200
