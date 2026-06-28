from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from app.core.exceptions import VectorStoreError

PAYLOAD_INDEX_FIELDS: dict[str, PayloadSchemaType] = {
    "document_id": PayloadSchemaType.KEYWORD,
    "category": PayloadSchemaType.KEYWORD,
    "language": PayloadSchemaType.KEYWORD,
    "document_version": PayloadSchemaType.INTEGER,
    "year": PayloadSchemaType.INTEGER,
    "filename": PayloadSchemaType.KEYWORD,
}


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    """Create collection with cosine distance and payload indexes if missing."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        _ensure_payload_indexes(client, collection_name)
        return

    info = client.get_collection(collection_name)
    params = info.config.params
    if params is None or params.vectors is None:
        raise VectorStoreError(f"Collection {collection_name} has no vector config")

    existing_size = params.vectors.size
    if existing_size != vector_size:
        raise VectorStoreError(
            f"Collection {collection_name} expects dimension {existing_size}, "
            f"got {vector_size}. Use a new QDRANT_COLLECTION for a different embedding model."
        )

    _ensure_payload_indexes(client, collection_name)


def _ensure_payload_indexes(client: QdrantClient, collection_name: str) -> None:
    for field_name, schema_type in PAYLOAD_INDEX_FIELDS.items():
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=schema_type,
            )
        except Exception:
            # Index may already exist on re-ingest
            continue
