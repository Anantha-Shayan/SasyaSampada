from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    CLEANING = "cleaning"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class LifecycleStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentCatalogEntry(BaseModel):
    document_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_]{2,127}$")
    title: str
    category: str
    source: str | None = None
    organization: str | None = None
    language: str = Field(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    year: int | None = Field(default=None, ge=1900, le=2100)
    filename: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]+\.pdf$")
    version: int = Field(ge=1, default=1)
    ingestion_status: IngestionStatus = IngestionStatus.PENDING
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    source_url: str | None = None
    content_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    file_size_bytes: int | None = Field(default=None, ge=0)
    page_count: int | None = Field(default=None, ge=0)
    chunk_count: int | None = Field(default=None, ge=0)
    embedding_model: str | None = None
    embedding_version: int | None = Field(default=None, ge=1)
    duplicate_of: str | None = None
    supersedes_document_id: str | None = None
    created_at: datetime
    updated_at: datetime
    indexed_at: datetime | None = None
    deleted_at: datetime | None = None
    last_error: str | None = None

    @field_validator("duplicate_of", "supersedes_document_id")
    @classmethod
    def validate_optional_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value[0].isalnum():
            raise ValueError("id must start with alphanumeric character")
        return value


class ChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    document_version: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    total_chunks: int = Field(ge=1)
    text: str
    token_count: int | None = Field(default=None, ge=0)
    char_count: int | None = Field(default=None, ge=0)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    section_title: str | None = None
    category: str
    language: str
    source: str | None = None
    source_url: str | None = None
    filename: str
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


class IngestionRunRecord(BaseModel):
    run_id: str
    document_id: str
    document_version: int
    started_at: datetime
    finished_at: datetime | None = None
    status: Literal["running", "success", "failed"]
    stages_completed: list[str] = Field(default_factory=list)
    error: str | None = None


class IngestionRegistry(BaseModel):
    runs: list[IngestionRunRecord] = Field(default_factory=list)
