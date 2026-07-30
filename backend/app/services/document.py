"""Compatibility shim — wraps KnowledgeBaseService for router."""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.knowledge_base import KnowledgeBaseService

_svc = KnowledgeBaseService()

async def sync_onedrive(db: AsyncSession) -> int:
    return await _svc.sync_onedrive(db)

async def process_document(doc_id, db: AsyncSession, file_bytes: bytes | None = None) -> bool:
    """Extract text from a stored Document's file and index it for search."""
    from app.models.document import Document

    doc = await db.get(Document, doc_id)
    if not doc:
        return False

    file_type = doc.file_type.value if hasattr(doc.file_type, "value") else str(doc.file_type)

    if file_bytes is None and doc.blob_url:
        from app.integrations.azure_blob import AzureBlobClient

        blob_client = AzureBlobClient()
        if not blob_client.use_mock:
            file_bytes = await blob_client.download_file(doc.blob_url)
        if not file_bytes:
            try:
                with open(doc.blob_url, "rb") as f:
                    file_bytes = f.read()
            except OSError:
                file_bytes = None

    content = await _svc.extract_text_from_file(file_bytes or b"", file_type)

    success = await _svc.index_document(str(doc.id), doc.name, content, file_type, {}, db)

    doc.ai_summary = content[:500] if content else doc.ai_summary
    doc.indexed_at = datetime.now(timezone.utc)
    await db.commit()
    return success

async def semantic_search_docs(query: str, top_k: int = 10, db: AsyncSession = None) -> list:
    """Semantic search — returns real Document rows directly (pgvector search
    now queries the Document table itself, see knowledge_base.py)."""
    return await _svc.search(query, top_k, {}, db)
