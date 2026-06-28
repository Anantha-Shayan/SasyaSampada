from __future__ import annotations

from datetime import datetime, timezone

from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import EmbeddedDocument, IndexedDocument

logger = get_logger(__name__)

DEFAULT_COLLECTION = "agri_knowledge"


class NoOpVectorStoreWriter:
    """
    Placeholder vector store writer — logs upsert intent without Qdrant.

    Replaced by Qdrant client in Phase 9.
    """

    stage_name = "vector_store"

    def __init__(self, collection_name: str = DEFAULT_COLLECTION) -> None:
        self.collection_name = collection_name

    def upsert(self, embedded: EmbeddedDocument) -> IndexedDocument:
        logger.info(
            "Would upsert %d vectors to collection '%s' for %s",
            len(embedded.chunks),
            self.collection_name,
            embedded.document_id,
        )

        return IndexedDocument(
            document_id=embedded.document_id,
            document_version=embedded.document_version,
            chunks_indexed=len(embedded.chunks),
            collection_name=self.collection_name,
            indexed_at=datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00")),
        )
