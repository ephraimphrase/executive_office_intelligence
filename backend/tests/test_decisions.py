import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_decisions_crud(client: AsyncClient):
    payload = {
        "description": "Approve Q3 Budget",
        "context": "Budget needs approval before next month",
        "made_by": "Board",
        "status": "PENDING_IMPLEMENTATION"
    }
    # Create
    response = await client.post("/api/decisions", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    decision_id = data["id"]
    
    # Get
    response = await client.get(f"/api/decisions/{decision_id}")
    assert response.status_code == 200
    
    # List
    response = await client.get("/api/decisions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_decisions_pending(client: AsyncClient):
    response = await client.get("/api/decisions/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
