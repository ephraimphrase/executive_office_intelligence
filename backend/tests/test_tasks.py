import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    response = await client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    payload = {
        "title": "New Task",
        "description": "Task description",
        "priority": "HIGH",
        "status": "TODO",
        "due_date": "2024-12-31T23:59:59Z"
    }
    response = await client.post("/api/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient):
    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/tasks/{random_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_kanban(client: AsyncClient):
    response = await client.get("/api/tasks/kanban")
    assert response.status_code == 200
    data = response.json()
    assert "TODO" in data
    assert "IN_PROGRESS" in data
    assert "DONE" in data
