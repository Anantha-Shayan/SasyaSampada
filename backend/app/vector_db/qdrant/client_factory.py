from __future__ import annotations

from qdrant_client import QdrantClient


def create_qdrant_client(url: str, api_key: str | None = None) -> QdrantClient:
    """Construct a Qdrant client from environment settings."""
    if api_key:
        return QdrantClient(url=url, api_key=api_key)
    return QdrantClient(url=url)
