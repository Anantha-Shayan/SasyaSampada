from __future__ import annotations

from datetime import datetime
from enum import Enum

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


class PageType(str, Enum):
    TEXT = "text"
    SCANNED = "scanned"
    MIXED = "mixed"


class ParsedTable(BaseModel):
    table_index: int = Field(ge=0)
    rows: list[list[str]]
    markdown: str
    row_count: int = Field(ge=0)
    col_count: int = Field(ge=0)


class ParsedPage(BaseModel):
    page_number: int = Field(ge=1)
    page_type: PageType = PageType.TEXT
    text: str
    body_text: str = ""
    header_text: str | None = None
    footer_text: str | None = None
    tables: list[ParsedTable] = Field(default_factory=list)
    has_tables: bool = False
    ocr_applied: bool = False
    needs_ocr: bool = False
    char_count: int = Field(ge=0)
    text_density: float | None = Field(default=None, ge=0.0)
    extraction_methods: list[str] = Field(default_factory=list)


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
    scanned_page_count: int = Field(default=0, ge=0)
    table_page_count: int = Field(default=0, ge=0)
    ocr_engine: str | None = None


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
