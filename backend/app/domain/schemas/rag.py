from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.schemas.retrieval import RetrievedChunk, RetrievalFilter


class Citation(BaseModel):
    citation_id: int = Field(ge=1)
    document_id: str
    title: str | None = None
    filename: str
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    section_title: str | None = None
    source_url: str | None = None
    score: float = Field(ge=0.0, le=1.0)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    filters: RetrievalFilter | None = None


class SearchResponse(BaseModel):
    success: bool = True
    query: str
    chunks: list[RetrievedChunk]
    citations: list[Citation]
    latency_ms: float
    request_id: str


class AskRequest(SearchRequest):
    language: str = Field(default="english", min_length=2, max_length=32)


class RAGTimings(BaseModel):
    retrieval_ms: float = 0.0
    context_ms: float = 0.0
    llm_ms: float = 0.0
    total_ms: float = 0.0


class AskResponse(BaseModel):
    success: bool = True
    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    timings: RAGTimings
    model: str
    request_id: str
    created_at: datetime
