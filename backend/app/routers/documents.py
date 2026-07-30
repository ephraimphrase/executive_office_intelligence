import uuid as uuid_lib
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.integrations.azure_blob import AzureBlobClient
from app.models.document import Document, DocumentVersion
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
)
from app.services.audit import log_action
from app.services.document import process_document, semantic_search_docs, sync_onedrive

router = APIRouter()


async def _store_file(file_bytes: bytes, category: str, subcategory: str, filename: str, content_type: str | None = None) -> str:
    """Persist bytes to Azure Blob Storage, falling back to local disk in dev
    when no connection string is configured. Returns the stored reference
    (blob name or local path) to save on the row."""
    safe_filename = filename.replace(" ", "_")
    blob_client = AzureBlobClient()
    blob_name = f"{category.upper()}/{subcategory.upper()}/{uuid_lib.uuid4()}_{safe_filename}"
    stored_ref = await blob_client.upload_file(file_bytes, blob_name, content_type=content_type)

    if not stored_ref:
        category_dir = Path("uploads") / category.upper() / subcategory.upper()
        category_dir.mkdir(parents=True, exist_ok=True)
        file_path = category_dir / safe_filename
        with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
        stored_ref = str(file_path)

    return stored_ref

@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    file_type: str | None = None,
    department: str | None = None,
    date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List documents with optional filters."""
    query = select(Document)
    if file_type:
        query = query.where(Document.file_type == file_type)
    if department:
        query = query.where(Document.department == department)
    if date:
        query = query.where(Document.created_at >= date)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=DocumentResponse)
async def create_document(
    doc_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create document metadata."""
    new_doc = Document(**doc_in.model_dump(exclude={"uploaded_by_id"}), uploaded_by_id=current_user.id)
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    department: str | None = Form(None),
    file_type: str | None = Form(None),
    category: str = Form("GENERAL"),
    subcategory: str = Form("UNCATEGORIZED"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload document (multipart form). Stored in Azure Blob Storage when
    AZURE_STORAGE_CONNECTION_STRING is configured (so it's covered by the
    storage account's redundancy/backup policy); falls back to local disk
    for dev when it isn't."""
    file_bytes = await file.read()
    size_bytes = len(file_bytes)
    stored_ref = await _store_file(file_bytes, category, subcategory, file.filename, file.content_type)

    new_doc = Document(
        name=file.filename,
        department=department,
        file_type=file_type or 'OTHER',
        category=category.upper(),
        subcategory=subcategory.upper(),
        size_bytes=size_bytes,
        blob_url=stored_ref,
        uploaded_by_id=current_user.id
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    await log_action(db, current_user, "DOCUMENT_UPLOAD", "Document", new_doc.id,
                      {"name": new_doc.name, "category": new_doc.category})

    # Process in background
    await process_document(new_doc.id, db)
    return new_doc

@router.post("/sync")
async def sync_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger OneDrive sync."""
    count = await sync_onedrive(db)
    return {"message": "OneDrive sync triggered", "new_document_count": count}

@router.get("/search", response_model=list[DocumentResponse])
async def search_documents(
    q: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Semantic search with query param q."""
    results = await semantic_search_docs(q, limit, db)
    return results

@router.get("/board-papers", response_model=list[DocumentResponse])
async def get_board_papers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List board papers."""
    query = select(Document).where(Document.is_board_paper == True)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/recent", response_model=list[DocumentResponse])
async def get_recent_documents(
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Recently added documents."""
    query = select(Document).order_by(Document.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get document detail."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: UUID,
    doc_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update document metadata."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    for field, value in doc_in.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
        
    await db.commit()
    await db.refresh(doc)
    return doc

@router.get("/{doc_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Version history for a document, newest first."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc_id)
        .order_by(DocumentVersion.version_number.desc())
    )
    return result.scalars().all()

@router.post("/{doc_id}/versions", response_model=DocumentVersionResponse)
async def upload_document_version(
    doc_id: UUID,
    file: UploadFile = File(...),
    change_note: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload a new revision of an existing document. The document's previous
    content is preserved as a DocumentVersion snapshot (created lazily on the
    first new version, if the original upload predates version tracking),
    then the new file becomes the document's current content."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    existing_versions = await db.execute(
        select(DocumentVersion).where(DocumentVersion.document_id == doc_id)
    )
    if not existing_versions.scalars().first() and doc.blob_url:
        db.add(DocumentVersion(
            document_id=doc.id,
            version_number=doc.version,
            name=doc.name,
            blob_url=doc.blob_url,
            size_bytes=doc.size_bytes,
            change_note="Initial version",
            uploaded_by_id=doc.uploaded_by_id,
        ))

    file_bytes = await file.read()
    stored_ref = await _store_file(
        file_bytes, doc.category or "GENERAL", doc.subcategory or "UNCATEGORIZED", file.filename, file.content_type
    )

    new_version_number = doc.version + 1
    new_version = DocumentVersion(
        document_id=doc.id,
        version_number=new_version_number,
        name=file.filename,
        blob_url=stored_ref,
        size_bytes=len(file_bytes),
        change_note=change_note,
        uploaded_by_id=current_user.id,
    )
    db.add(new_version)

    doc.blob_url = stored_ref
    doc.name = file.filename
    doc.size_bytes = len(file_bytes)
    doc.version = new_version_number

    await db.commit()
    await db.refresh(new_version)
    await log_action(db, current_user, "DOCUMENT_NEW_VERSION", "Document", doc.id,
                      {"name": doc.name, "version": new_version_number})

    await process_document(doc.id, db)
    return new_version

@router.get("/{doc_id}/versions/{version_id}/download")
async def download_document_version(
    doc_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Download a historical revision's file content."""
    from fastapi.responses import Response

    version = await db.get(DocumentVersion, version_id)
    if not version or version.document_id != doc_id:
        raise HTTPException(status_code=404, detail="Version not found")
    if not version.blob_url:
        raise HTTPException(status_code=404, detail="This version has no stored file content")

    blob_client = AzureBlobClient()
    file_bytes = b""
    if not blob_client.use_mock:
        file_bytes = await blob_client.download_file(version.blob_url)
    if not file_bytes:
        try:
            with open(version.blob_url, "rb") as f:
                file_bytes = f.read()
        except OSError:
            raise HTTPException(status_code=404, detail="Stored file content is unavailable")

    return Response(
        content=file_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{version.name}"'},
    )

@router.post("/{doc_id}/summarize", response_model=DocumentResponse)
async def summarize_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Regenerate AI summary."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Trigger re-summarization
    doc.ai_summary = "New AI Generated Summary based on content."
    await db.commit()
    await db.refresh(doc)
    return doc

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete document."""
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    blob_client = AzureBlobClient()
    if not blob_client.use_mock and doc.blob_url:
        await blob_client.delete_file(doc.blob_url)

    await db.delete(doc)
    await db.commit()
    await log_action(db, current_user, "DOCUMENT_DELETE", "Document", doc_id, {"name": doc.name})
    return {"message": "Document deleted successfully"}
