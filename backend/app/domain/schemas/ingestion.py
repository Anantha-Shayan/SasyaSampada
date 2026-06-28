from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.schemas.knowledge_base import ChunkRecord, DocumentCatalogEntry


class LoadedDocument(BaseModel):
    catalog: DocumentCatalogEntry
    source_path: str
    content_sha256: str
    file_size_bytes: int


class ValidatedDocument(BaseModel):
    loaded: LoadedDocument
    mime_type: str = "application/pdf"
    validated_at: datetime


class ParsedPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    has_tables: bool = False
    ocr_applied: bool = False
    char_count: int = Field(ge=0)


class ParsedDocumentArtifact(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    pages: list[ParsedPage]
    page_count: int = Field(ge=0)
    parser_name: str
    parser_version: str
    parsed_at: datetime
    source_filename: str
    content_sha256: str


class CleanedDocument(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    text: str
    char_count: int = Field(ge=0)
    cleaner_name: str
    cleaned_at: datetime


class TextChunk(BaseModel):
    chunk_index: int = Field(ge=0)
    text: str
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)


class ChunkedDocument(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    chunks: list[TextChunk]
    chunk_size: int
    chunk_overlap: int


class MetadataBundle(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    chunks: list[ChunkRecord]
    document_meta: dict[str, object]


class EmbeddedChunk(BaseModel):
    chunk: ChunkRecord
    vector: list[float]
    embedding_model: str


class EmbeddedDocument(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    chunks: list[EmbeddedChunk]
    embedding_model: str
    dimension: int


class IndexedDocument(BaseModel):
    document_id: str
    document_version: int = Field(ge=1)
    chunks_indexed: int
    collection_name: str
    indexed_at: datetime
