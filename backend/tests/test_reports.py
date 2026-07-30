import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reports_generate(client: AsyncClient):
    response = await client.get("/api/reports/executive-summary?start_date=2024-01-01&end_date=2024-01-31")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

@pytest.mark.asyncio
async def test_reports_task_completion(client: AsyncClient):
    response = await client.get("/api/reports/task-completion")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
