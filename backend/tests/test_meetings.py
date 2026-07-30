import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient):
    payload = {
        "title": "Strategy Meeting",
        "meeting_date": "2024-10-15",
        "meeting_type": "DEPARTMENT",
        "status": "SCHEDULED"
    }
    response = await client.post("/api/meetings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Strategy Meeting"
    assert data["meeting_type"] == "DEPARTMENT"
    assert "id" in data
    
    # Test get meeting
    meeting_id = data["id"]
    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Strategy Meeting"

@pytest.mark.asyncio
async def test_get_meetings(client: AsyncClient):
    response = await client.get("/api/meetings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_update_meeting(client: AsyncClient):
    # Create first
    payload = {
        "title": "Initial Meeting",
        "meeting_date": "2024-10-15"
    }
    response = await client.post("/api/meetings", json=payload)
    assert response.status_code == 200
    meeting_id = response.json()["id"]
    
    # Update
    update_payload = {
        "status": "COMPLETED"
    }
    response = await client.put(f"/api/meetings/{meeting_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"
