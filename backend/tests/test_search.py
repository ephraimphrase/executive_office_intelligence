import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient):
    response = await client.get("/api/search?q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
