from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone

from app.core.exceptions import MetadataError
from app.core.logging import get_logger, utc_now_iso
from app.domain.schemas.ingestion import (
    ChunkedDocument,
    MetadataBundle,
    ParsedDocumentArtifact,
)
from app.domain.schemas.knowledge_base import ChunkRecord, DocumentCatalogEntry
from app.ingestion.stages.metadata.page_mapper import map_chunk_to_pages
from app.ingestion.stages.metadata.section_detector import (
    detect_section_title,
    estimate_token_count,
)
from app.knowledge_base.paths import chunks_jsonl_path, document_meta_path, make_chunk_id

logger = get_logger(__name__)

METADATA_GENERATOR_NAME = "rich_v1"
METADATA_SCHEMA_VERSION = "1.0"


class RichMetadataGenerator:
    """
    Attach rich, filterable metadata to each chunk for retrieval and citations.

    Fields: document_id, chunk_id, chunk_index, filename, pages, section_title,
    source, language, timestamps, and extensible document_meta envelope.
    """

    stage_name = "metadata"

    def __init__(
        self,
        parsed_loader: Callable[[str, int], ParsedDocumentArtifact | None] | None = None,
    ) -> None:
        self._parsed_loader = parsed_loader or self._default_parsed_loader

    @staticmethod
    def _default_parsed_loader(
        document_id: str,
        document_version: int,
    ) -> ParsedDocumentArtifact | None:
        from app.ingestion.stages.parser import CompositePdfParser

        return CompositePdfParser.load_cached(document_id, document_version)

    def generate(
        self,
        chunked: ChunkedDocument,
        catalog: DocumentCatalogEntry,
    ) -> MetadataBundle:
        logger.info("Generating rich metadata for %s", chunked.document_id)

        try:
            parsed = self._parsed_loader(
                chunked.document_id,
                chunked.document_version,
            )
            total = len(chunked.chunks)
            created_at = datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00"))
            records: list[ChunkRecord] = []

            for chunk in chunked.chunks:
                page_start, page_end = chunk.page_start, chunk.page_end
                if page_start is None or page_end is None:
                    mapped_start, mapped_end = map_chunk_to_pages(chunk.text, parsed)
                    page_start = page_start or mapped_start
                    page_end = page_end or mapped_end

                section_title = detect_section_title(chunk.text)
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
                        token_count=estimate_token_count(chunk.text),
                        char_count=len(chunk.text),
                        page_start=page_start,
                        page_end=page_end,
                        section_title=section_title,
                        title=catalog.title,
                        organization=catalog.organization,
                        year=catalog.year,
                        category=catalog.category,
                        language=catalog.language,
                        source=catalog.source,
                        source_url=catalog.source_url,
                        filename=catalog.filename,
                        content_hash=content_hash,
                        chunker_name=chunked.chunker_name,
                        metadata_schema_version=METADATA_SCHEMA_VERSION,
                        created_at=created_at,
                        ingested_at=created_at,
                    )
                )

            document_meta: dict[str, object] = {
                "schema_version": METADATA_SCHEMA_VERSION,
                "document_id": chunked.document_id,
                "document_version": chunked.document_version,
                "chunk_count": total,
                "chunk_size": chunked.chunk_size,
                "chunk_overlap": chunked.chunk_overlap,
                "chunker_name": chunked.chunker_name,
                "metadata_generator": METADATA_GENERATOR_NAME,
                "category": catalog.category,
                "language": catalog.language,
                "title": catalog.title,
                "organization": catalog.organization,
                "year": catalog.year,
                "filename": catalog.filename,
                "source": catalog.source,
                "source_url": catalog.source_url,
                "content_sha256": catalog.content_sha256,
                "generated_at": utc_now_iso(),
                "ext": {
                    "filterable_fields": [
                        "document_id",
                        "category",
                        "language",
                        "year",
                        "page_start",
                        "page_end",
                        "section_title",
                        "filename",
                    ],
                    "future_fields": [
                        "crop_type",
                        "season",
                        "state",
                        "district",
                        "confidence_score",
                        "ocr_applied",
                    ],
                },
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
        logger.info("Wrote %d chunk records to %s", len(bundle.chunks), jsonl_path)


# Backward-compatible alias
DefaultMetadataGenerator = RichMetadataGenerator
