from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievalFilter(BaseModel):
    """Optional metadata filters applied at Qdrant query time."""

    document_id: str | None = None
    category: str | None = None
    language: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)


class RetrievedChunk(BaseModel):
    """A single chunk returned from similarity search with score and citation fields."""

    chunk_id: str
    document_id: str
    document_version: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    text: str
    score: float = Field(ge=0.0, le=1.0)
    category: str
    language: str
    filename: str
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    section_title: str | None = None
    title: str | None = None
    organization: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    source: str | None = None
    source_url: str | None = None


class RetrievalResult(BaseModel):
    """Outcome of a retriever call for logging and RAG context assembly."""

    query: str
    chunks: list[RetrievedChunk]
    top_k: int = Field(ge=1)
    score_threshold: float = Field(ge=0.0, le=1.0)
    embedding_model: str
    filters_applied: RetrievalFilter | None = None
