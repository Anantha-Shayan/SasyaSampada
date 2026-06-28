from __future__ import annotations

from datetime import datetime, timezone

from qdrant_client import QdrantClient

from app.core.exceptions import VectorStoreError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import EmbeddedDocument, IndexedDocument
from app.vector_db.base import VectorStore
from app.vector_db.qdrant import QdrantVectorStore, create_qdrant_client

logger = get_logger(__name__)

DEFAULT_COLLECTION = "agri_knowledge"


class QdrantVectorStoreWriter:
    """Ingestion stage — upsert embedded chunks into Qdrant."""

    stage_name = "vector_store"

    def __init__(
        self,
        store: VectorStore | None = None,
        *,
        collection_name: str | None = None,
        url: str | None = None,
        api_key: str | None = None,
        upsert_batch_size: int | None = None,
        client: QdrantClient | None = None,
    ) -> None:
        from app.config import (
            QDRANT_API_KEY,
            QDRANT_COLLECTION,
            QDRANT_UPSERT_BATCH_SIZE,
            QDRANT_URL,
        )

        resolved_collection = collection_name or QDRANT_COLLECTION
        resolved_batch_size = (
            upsert_batch_size
            if upsert_batch_size is not None
            else QDRANT_UPSERT_BATCH_SIZE
        )

        if store is not None:
            self._store = store
            self.collection_name = store.collection_name
            return

        if client is None:
            client = create_qdrant_client(
                url or QDRANT_URL,
                api_key if api_key is not None else QDRANT_API_KEY,
            )

        self._store = QdrantVectorStore(
            client,
            resolved_collection,
            upsert_batch_size=resolved_batch_size,
        )
        self.collection_name = resolved_collection

    def upsert(self, embedded: EmbeddedDocument) -> IndexedDocument:
        logger.info(
            "Indexing %d vectors to Qdrant collection '%s' for %s",
            len(embedded.chunks),
            self.collection_name,
            embedded.document_id,
        )

        try:
            chunks_indexed = self._store.upsert_document(embedded)
        except VectorStoreError:
            raise
        except Exception as exc:
            raise VectorStoreError(
                f"Failed to index {embedded.document_id} in Qdrant",
                stage=self.stage_name,
            ) from exc

        return IndexedDocument(
            document_id=embedded.document_id,
            document_version=embedded.document_version,
            chunks_indexed=chunks_indexed,
            collection_name=self.collection_name,
            indexed_at=datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00")),
        )
