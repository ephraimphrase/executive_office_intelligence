from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentAccessLevel, FileType


class DocumentBase(BaseModel):
    name: str
    file_type: FileType = FileType.OTHER
    onedrive_id: str | None = None
    blob_url: str | None = None
    size_bytes: int | None = None
    department: str | None = None
    category: str | None = "GENERAL"
    subcategory: str | None = "UNCATEGORIZED"
    ai_summary: str | None = None
    key_topics: list[str] = []
    vector_ids: list[str] = []
    onedrive_path: str | None = None
    is_board_paper: bool = False
    is_policy: bool = False
    is_contract: bool = False
    access_level: DocumentAccessLevel = DocumentAccessLevel.INTERNAL
    version: int = 1

class DocumentCreate(DocumentBase):
    uploaded_by_id: UUID | None = None
    meeting_id: UUID | None = None

class DocumentUpdate(BaseModel):
    name: str | None = None
    department: str | None = None
    category: str | None = None
    subcategory: str | None = None
    is_board_paper: bool | None = None
    is_policy: bool | None = None
    is_contract: bool | None = None
    access_level: DocumentAccessLevel | None = None
    ai_summary: str | None = None
    key_topics: list[str] | None = None

class DocumentSummaryUpdate(BaseModel):
    ai_summary: str
    key_topics: list[str]

class DocumentResponse(DocumentBase):
    id: UUID
    uploaded_by_id: UUID | None
    meeting_id: UUID | None
    indexed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentList(BaseModel):
    items: list[DocumentResponse]
    total: int
    skip: int
    limit: int

class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    name: str
    size_bytes: int | None
    change_note: str | None
    uploaded_by_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
