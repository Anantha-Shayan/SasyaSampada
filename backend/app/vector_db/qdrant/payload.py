from __future__ import annotations

from app.domain.schemas.knowledge_base import ChunkRecord


def chunk_record_to_payload(record: ChunkRecord, *, embedding_model: str) -> dict[str, object]:
    """Build Qdrant payload for filtered search and citation-ready retrieval."""
    payload: dict[str, object] = {
        "chunk_id": record.chunk_id,
        "document_id": record.document_id,
        "document_version": record.document_version,
        "chunk_index": record.chunk_index,
        "total_chunks": record.total_chunks,
        "text": record.text,
        "category": record.category,
        "language": record.language,
        "filename": record.filename,
        "content_hash": record.content_hash,
        "embedding_model": embedding_model,
        "metadata_schema_version": record.metadata_schema_version,
    }

    optional_fields = {
        "page_start": record.page_start,
        "page_end": record.page_end,
        "section_title": record.section_title,
        "title": record.title,
        "organization": record.organization,
        "year": record.year,
        "source": record.source,
        "source_url": record.source_url,
        "chunker_name": record.chunker_name,
        "token_count": record.token_count,
        "char_count": record.char_count,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value

    return payload
