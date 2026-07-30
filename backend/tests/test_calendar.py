import pytest
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
async def test_calendar_crud(client: AsyncClient):
    payload = {
        "title": "Board Meeting",
        "start_datetime": "2024-11-01T10:00:00Z",
        "end_datetime": "2024-11-01T12:00:00Z",
        "event_type": "BOARD",
        "priority": "HIGH",
        "status": "SCHEDULED",
        "owner_id": "00000000-0000-0000-0000-000000000000"
    }
    response = await client.post("/api/calendar/events", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    event_id = data["id"]
    
    response = await client.get(f"/api/calendar/events/{event_id}")
    assert response.status_code == 200
    
    response = await client.get("/api/calendar/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    response = await client.put(f"/api/calendar/events/{event_id}", json={"title": "Updated Meeting"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Meeting"

@pytest.mark.asyncio
async def test_calendar_upcoming(client: AsyncClient):
    response = await client.get("/api/calendar/upcoming-board")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
