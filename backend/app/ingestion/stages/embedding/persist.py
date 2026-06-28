from __future__ import annotations

import json

from app.core.logging import get_logger, utc_now_iso
from app.knowledge_base.paths import embeddings_dir

logger = get_logger(__name__)


def persist_embeddings(
    *,
    document_id: str,
    document_version: int,
    embedding_model: str,
    dimension: int,
    vectors: list[tuple[str, list[float]]],
    batch_size: int,
    normalize: bool,
) -> None:
    """Write vectors.jsonl and embedding_meta.json under data/embeddings/."""
    out_dir = embeddings_dir(document_id, document_version, embedding_model)
    out_dir.mkdir(parents=True, exist_ok=True)

    vectors_path = out_dir / "vectors.jsonl"
    with vectors_path.open("w", encoding="utf-8") as handle:
        for chunk_id, vector in vectors:
            handle.write(
                json.dumps({"chunk_id": chunk_id, "vector": vector}, separators=(",", ":"))
                + "\n"
            )

    meta = {
        "document_id": document_id,
        "document_version": document_version,
        "embedding_model": embedding_model,
        "dimension": dimension,
        "chunk_count": len(vectors),
        "batch_size": batch_size,
        "normalize": normalize,
        "generated_at": utc_now_iso(),
    }
    meta_path = out_dir / "embedding_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote %d vectors to %s", len(vectors), vectors_path)
