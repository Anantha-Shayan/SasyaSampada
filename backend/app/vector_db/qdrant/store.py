from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from app.core.exceptions import RetryableIngestionError, VectorStoreError
from app.core.logging import get_logger
from app.domain.schemas.ingestion import EmbeddedDocument
from app.vector_db.qdrant.collection import ensure_collection
from app.vector_db.qdrant.payload import chunk_record_to_payload
from app.vector_db.qdrant.point_ids import chunk_id_to_point_id

logger = get_logger(__name__)


class QdrantVectorStore:
    """Qdrant-backed vector store for ingestion upserts and future retrieval."""

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        *,
        upsert_batch_size: int = 64,
    ) -> None:
        self._client = client
        self.collection_name = collection_name
        self._upsert_batch_size = upsert_batch_size

    def upsert_document(self, embedded: EmbeddedDocument) -> int:
        if not embedded.chunks:
            return 0

        try:
            ensure_collection(
                self._client,
                self.collection_name,
                embedded.dimension,
            )
            self._delete_points_for_version(
                embedded.document_id,
                embedded.document_version,
            )

            points = [
                PointStruct(
                    id=chunk_id_to_point_id(item.chunk.chunk_id),
                    vector=item.vector,
                    payload=chunk_record_to_payload(
                        item.chunk,
                        embedding_model=embedded.embedding_model,
                    ),
                )
                for item in embedded.chunks
            ]

            for start in range(0, len(points), self._upsert_batch_size):
                batch = points[start : start + self._upsert_batch_size]
                self._client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=True,
                )

            logger.info(
                "Upserted %d points to %s for %s v%d",
                len(points),
                self.collection_name,
                embedded.document_id,
                embedded.document_version,
            )
            return len(points)
        except VectorStoreError:
            raise
        except Exception as exc:
            if _is_retryable_qdrant_error(exc):
                raise RetryableIngestionError(
                    f"Transient Qdrant error upserting {embedded.document_id}",
                    stage="vector_store",
                ) from exc
            raise VectorStoreError(
                f"Failed to upsert {embedded.document_id} to Qdrant",
            ) from exc

    def delete_document_version(self, document_id: str, document_version: int) -> None:
        if not self._client.collection_exists(self.collection_name):
            return
        self._delete_points_for_version(document_id, document_version)

    def _delete_points_for_version(self, document_id: str, document_version: int) -> None:
        try:
            self._client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        ),
                        FieldCondition(
                            key="document_version",
                            match=MatchValue(value=document_version),
                        ),
                    ]
                ),
                wait=True,
            )
        except Exception as exc:
            if _is_retryable_qdrant_error(exc):
                raise RetryableIngestionError(
                    f"Transient Qdrant error deleting {document_id} v{document_version}",
                    stage="vector_store",
                ) from exc
            raise VectorStoreError(
                f"Failed to delete {document_id} v{document_version} from Qdrant",
            ) from exc


def _is_retryable_qdrant_error(exc: Exception) -> bool:
    message = str(exc).lower()
    retry_tokens = (
        "timeout",
        "connection",
        "temporarily",
        "unavailable",
        "503",
        "502",
        "504",
    )
    return any(token in message for token in retry_tokens)
