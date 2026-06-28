from __future__ import annotations

from app.core.exceptions import RetrievalError
from app.domain.schemas.retrieval import RetrievedChunk


def payload_to_retrieved_chunk(score: float, payload: dict[str, object]) -> RetrievedChunk:
    """Map a Qdrant hit payload into a typed RetrievedChunk."""
    try:
        return RetrievedChunk(
            chunk_id=str(payload["chunk_id"]),
            document_id=str(payload["document_id"]),
            document_version=int(payload["document_version"]),
            chunk_index=int(payload["chunk_index"]),
            text=str(payload["text"]),
            score=float(score),
            category=str(payload["category"]),
            language=str(payload["language"]),
            filename=str(payload["filename"]),
            page_start=_optional_int(payload.get("page_start")),
            page_end=_optional_int(payload.get("page_end")),
            section_title=_optional_str(payload.get("section_title")),
            title=_optional_str(payload.get("title")),
            organization=_optional_str(payload.get("organization")),
            year=_optional_int(payload.get("year")),
            source=_optional_str(payload.get("source")),
            source_url=_optional_str(payload.get("source_url")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RetrievalError("Invalid Qdrant payload for retrieved chunk") from exc


def _optional_str(value: object | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    return int(value)
