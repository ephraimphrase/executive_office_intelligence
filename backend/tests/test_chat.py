import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_history(client: AsyncClient):
    response = await client.get("/api/chat/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_chat_message(client: AsyncClient):
    payload = {
        "message": "Hello",
        "context": None,
        "include_documents": False
    }
    response = await client.post("/api/chat/message", json=payload)
    assert response.status_code == 200
    assert "reply" in response.json()
