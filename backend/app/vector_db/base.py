from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.schemas.ingestion import EmbeddedDocument


@runtime_checkable
class VectorStore(Protocol):
    """Vector database operations shared by ingestion and retrieval."""

    collection_name: str

    def upsert_document(self, embedded: EmbeddedDocument) -> int: ...

    def delete_document_version(self, document_id: str, document_version: int) -> None: ...
