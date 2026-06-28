from __future__ import annotations

import uuid

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def chunk_id_to_point_id(chunk_id: str) -> str:
    """Stable Qdrant point id from canonical chunk_id (idempotent upserts)."""
    return str(uuid.uuid5(_NAMESPACE, chunk_id))
