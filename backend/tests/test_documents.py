import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_document(client: AsyncClient):
    payload = {
        "name": "Q4 Report.pdf",
        "file_type": "PDF",
        "department": "Finance"
    }
    response = await client.post("/api/documents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Q4 Report.pdf"
    assert data["file_type"] == "PDF"
    assert "id" in data
    
    # Test get document
    doc_id = data["id"]
    response = await client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Q4 Report.pdf"

@pytest.mark.asyncio
async def test_get_documents(client: AsyncClient):
    response = await client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_update_document(client: AsyncClient):
    # Create first
    payload = {
        "name": "Initial Document.docx",
        "file_type": "WORD"
    }
    response = await client.post("/api/documents", json=payload)
    assert response.status_code == 200
    doc_id = response.json()["id"]
    
    # Update
    update_payload = {
        "department": "HR",
        "is_board_paper": True
    }
    response = await client.put(f"/api/documents/{doc_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["department"] == "HR"
    assert response.json()["is_board_paper"] is True
