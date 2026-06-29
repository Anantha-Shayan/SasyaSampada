from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import IngestionLogWriter, utc_now_iso
from app.domain.schemas.ingestion import IndexedDocument
from app.domain.schemas.knowledge_base import DocumentCatalogEntry, IngestionStatus
from app.knowledge_base.paths import DOCUMENTS_MANIFEST, INGESTION_REGISTRY, ingestion_log_path
from app.knowledge_base.registry import get_document, load_catalog, save_catalog


@dataclass
class IngestionContext:
    document_id: str
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    catalog_entry: DocumentCatalogEntry | None = None
    log_writer: IngestionLogWriter | None = None
    stages_completed: list[str] = field(default_factory=list)


@dataclass
class IngestionResult:
    success: bool
    document_id: str
    run_id: str
    stages_completed: list[str]
    indexed: IndexedDocument | None = None
    error: str | None = None
    duration_ms: int | None = None


def _utc_now() -> datetime:
    return datetime.fromisoformat(utc_now_iso().replace("Z", "+00:00"))


def _update_catalog_entry(
    document_id: str,
    *,
    ingestion_status: IngestionStatus | None = None,
    last_error: str | None = None,
    page_count: int | None = None,
    chunk_count: int | None = None,
    embedding_model: str | None = None,
    indexed: bool = False,
    content_sha256: str | None = None,
    file_size_bytes: int | None = None,
) -> DocumentCatalogEntry:
    entries = load_catalog()
    updated: DocumentCatalogEntry | None = None

    for index, entry in enumerate(entries):
        if entry.document_id != document_id:
            continue
        data = entry.model_dump()
        if ingestion_status is not None:
            data["ingestion_status"] = ingestion_status
        if last_error is not None:
            data["last_error"] = last_error
        if page_count is not None:
            data["page_count"] = page_count
        if chunk_count is not None:
            data["chunk_count"] = chunk_count
        if embedding_model is not None:
            data["embedding_model"] = embedding_model
        if content_sha256 is not None:
            data["content_sha256"] = content_sha256
        if file_size_bytes is not None:
            data["file_size_bytes"] = file_size_bytes
        if indexed:
            data["indexed_at"] = _utc_now()
            data["last_error"] = None
        data["updated_at"] = _utc_now()
        updated = DocumentCatalogEntry.model_validate(data)
        entries[index] = updated
        break

    if updated is None:
        raise ValueError(f"Document not found in catalog: {document_id}")

    save_catalog(entries)
    return updated


def _append_registry_run(
    document_id: str,
    document_version: int,
    run_id: str,
    status: str,
    stages_completed: list[str],
    error: str | None = None,
) -> None:
    if INGESTION_REGISTRY.exists():
        payload = json.loads(INGESTION_REGISTRY.read_text(encoding="utf-8"))
    else:
        payload = {"runs": []}

    payload["runs"].append(
        {
            "run_id": run_id,
            "document_id": document_id,
            "document_version": document_version,
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "status": status,
            "stages_completed": stages_completed,
            "error": error,
        }
    )
    INGESTION_REGISTRY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
