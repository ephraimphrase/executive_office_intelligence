import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base, _is_sqlite

# text-embedding-3-large produces 3072-dim vectors (see app/integrations/openai_client.py).
EMBEDDING_DIM = 3072

if _is_sqlite:
    # pgvector's Vector type only compiles against the postgres dialect —
    # SQLite dev mode stores the same embedding as a plain JSON float array
    # and falls back to a Python-side cosine scan (see knowledge_base.py).
    _EmbeddingType = JSON
else:
    from pgvector.sqlalchemy import Vector
    _EmbeddingType = Vector(EMBEDDING_DIM)


class FileType(str, enum.Enum):
    WORD = "WORD"
    PDF = "PDF"
    EXCEL = "EXCEL"
    POWERPOINT = "POWERPOINT"
    OTHER = "OTHER"

class DocumentAccessLevel(str, enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    file_type = Column(Enum(FileType), nullable=False, default=FileType.OTHER)
    
    onedrive_id = Column(String, nullable=True, unique=True, index=True)
    blob_url = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    category = Column(String, nullable=True, default="GENERAL")
    subcategory = Column(String, nullable=True, default="UNCATEGORIZED")
    
    ai_summary = Column(Text, nullable=True)
    key_topics = Column(JSON, default=list)
    indexed_at = Column(DateTime, nullable=True)
    vector_ids = Column(JSON, default=list)  # legacy — unused now that embeddings live on this row directly
    embedding = Column(_EmbeddingType, nullable=True)
    onedrive_path = Column(String, nullable=True)
    
    is_board_paper = Column(Boolean, default=False)
    is_policy = Column(Boolean, default=False)
    is_contract = Column(Boolean, default=False)
    access_level = Column(Enum(DocumentAccessLevel), nullable=False, default=DocumentAccessLevel.INTERNAL)

    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    meeting_id = Column(UUID(as_uuid=True), nullable=True) # Would link to meeting_records.id

    # Current version number — bumped each time a new revision is uploaded
    # via POST /documents/{id}/versions. Historical revisions live in
    # DocumentVersion, keyed by document_id.
    version = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])


class DocumentVersion(Base):
    """Immutable snapshot of a Document's content at a point in time."""
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)

    name = Column(String, nullable=False)
    blob_url = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    change_note = Column(Text, nullable=True)

    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", foreign_keys=[document_id], backref="versions")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
