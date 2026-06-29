from __future__ import annotations

from app.domain.schemas.rag import Citation
from app.domain.schemas.retrieval import RetrievedChunk


def citations_from_chunks(chunks: list[RetrievedChunk]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[str] = set()
    for chunk in chunks:
        if chunk.chunk_id in seen:
            continue
        seen.add(chunk.chunk_id)
        citations.append(
            Citation(
                citation_id=len(citations) + 1,
                document_id=chunk.document_id,
                title=chunk.title,
                filename=chunk.filename,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                section_title=chunk.section_title,
                source_url=chunk.source_url,
                score=chunk.score,
            )
        )
    return citations
