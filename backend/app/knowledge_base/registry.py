from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterator

from pydantic import TypeAdapter

from app.domain.schemas.knowledge_base import DocumentCatalogEntry
from app.knowledge_base.paths import DOCUMENTS_MANIFEST

_catalog_adapter = TypeAdapter(list[DocumentCatalogEntry])


def load_catalog(manifest_path: Path | None = None) -> list[DocumentCatalogEntry]:
    path = manifest_path or DOCUMENTS_MANIFEST
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _catalog_adapter.validate_python(raw)


def save_catalog(entries: list[DocumentCatalogEntry], manifest_path: Path | None = None) -> None:
    path = manifest_path or DOCUMENTS_MANIFEST
    payload = [entry.model_dump(mode="json") for entry in entries]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def get_document(
    document_id: str,
    manifest_path: Path | None = None,
) -> DocumentCatalogEntry | None:
    for entry in load_catalog(manifest_path):
        if entry.document_id == document_id:
            return entry
    return None


def iter_active_documents(
    manifest_path: Path | None = None,
) -> Iterator[DocumentCatalogEntry]:
    for entry in load_catalog(manifest_path):
        if entry.lifecycle_status == "active" and entry.duplicate_of is None:
            yield entry


def compute_file_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_duplicate_by_hash(
    content_sha256: str,
    manifest_path: Path | None = None,
    *,
    exclude_document_id: str | None = None,
) -> DocumentCatalogEntry | None:
    for entry in load_catalog(manifest_path):
        if exclude_document_id and entry.document_id == exclude_document_id:
            continue
        if entry.content_sha256 == content_sha256 and entry.lifecycle_status != "deleted":
            return entry
    return None
