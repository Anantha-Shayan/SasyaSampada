from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from app.core.exceptions import MetadataError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import ChunkedDocument, MetadataBundle
from app.domain.schemas.knowledge_base import ChunkRecord, DocumentCatalogEntry
from app.knowledge_base.paths import chunks_jsonl_path, document_meta_path, make_chunk_id

logger = get_logger(__name__)

METADATA_GENERATOR_NAME = "default"


class DefaultMetadataGenerator:
    """Attach catalog fields and stable chunk ids to each text chunk."""

    stage_name = "metadata"

    def generate(
        self,
        chunked: ChunkedDocument,
        catalog: DocumentCatalogEntry,
    ) -> MetadataBundle:
        logger.info("Generating metadata for %s", chunked.document_id)

        try:
            total = len(chunked.chunks)
            created_at = datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00"))
            records: list[ChunkRecord] = []

            for chunk in chunked.chunks:
                chunk_id = make_chunk_id(
                    chunked.document_id,
                    chunked.document_version,
                    chunk.chunk_index,
                )
                content_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
                records.append(
                    ChunkRecord(
                        chunk_id=chunk_id,
                        document_id=chunked.document_id,
                        document_version=chunked.document_version,
                        chunk_index=chunk.chunk_index,
                        total_chunks=total,
                        text=chunk.text,
                        char_count=len(chunk.text),
                        page_start=chunk.page_start,
                        page_end=chunk.page_end,
                        category=catalog.category,
                        language=catalog.language,
                        source=catalog.source,
                        source_url=catalog.source_url,
                        filename=catalog.filename,
                        content_hash=content_hash,
                        created_at=created_at,
                    )
                )

            document_meta = {
                "document_id": chunked.document_id,
                "document_version": chunked.document_version,
                "chunk_count": total,
                "chunk_size": chunked.chunk_size,
                "chunk_overlap": chunked.chunk_overlap,
                "metadata_generator": METADATA_GENERATOR_NAME,
                "category": catalog.category,
                "language": catalog.language,
                "title": catalog.title,
                "generated_at": utc_now_iso(),
            }

            bundle = MetadataBundle(
                document_id=chunked.document_id,
                document_version=chunked.document_version,
                chunks=records,
                document_meta=document_meta,
            )
            self._persist(bundle)
            return bundle
        except Exception as exc:
            raise MetadataError(
                f"Failed to generate metadata for {chunked.document_id}",
                stage=self.stage_name,
            ) from exc

    def _persist(self, bundle: MetadataBundle) -> None:
        jsonl_path = chunks_jsonl_path(bundle.document_id, bundle.document_version)
        meta_path = document_meta_path(bundle.document_id, bundle.document_version)
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)

        with jsonl_path.open("w", encoding="utf-8") as handle:
            for record in bundle.chunks:
                handle.write(record.model_dump_json() + "\n")

        meta_path.write_text(
            json.dumps(bundle.document_meta, indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("Wrote metadata to %s", jsonl_path)
