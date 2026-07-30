import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_commitments_crud(client: AsyncClient):
    payload = {
        "description": "Ensure Q3 reports are finalized",
        "source_type": "MEETING",
        "deadline": "2024-12-01T00:00:00Z",
        "status": "PENDING"
    }
    # Create
    response = await client.post("/api/commitments", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    commitment_id = data["id"]
    
    # Get
    response = await client.get(f"/api/commitments/{commitment_id}")
    assert response.status_code == 200
    
    # List
    response = await client.get("/api/commitments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_commitments_overdue(client: AsyncClient):
    response = await client.get("/api/commitments/overdue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_commitments_by_status(client: AsyncClient):
    response = await client.get("/api/commitments?status=PENDING")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
