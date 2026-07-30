import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_emails_crud(client: AsyncClient):
    # Actually email creation might not have an endpoint since they are polled, but there might be a CRUD.
    # Let's just list emails.
    response = await client.get("/api/emails")
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_emails_critical(client: AsyncClient):
    response = await client.get("/api/emails/critical")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
