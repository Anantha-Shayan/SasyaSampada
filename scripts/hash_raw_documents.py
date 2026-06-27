"""Populate content_sha256 and file_size_bytes in documents.json from data/raw/."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.knowledge_base.paths import DOCUMENTS_MANIFEST, RAW_DIR  # noqa: E402
from app.knowledge_base.registry import (  # noqa: E402
    compute_file_sha256,
    find_duplicate_by_hash,
    load_catalog,
    save_catalog,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    entries = load_catalog()
    updated = 0

    for entry in entries:
        pdf_path = RAW_DIR / entry.filename
        if not pdf_path.exists():
            print(f"skip (missing): {entry.filename}")
            continue

        sha256 = compute_file_sha256(pdf_path)
        size = pdf_path.stat().st_size

        if entry.content_sha256 == sha256 and entry.file_size_bytes == size:
            continue

        duplicate = find_duplicate_by_hash(sha256, exclude_document_id=entry.document_id)
        if duplicate:
            entry.duplicate_of = duplicate.document_id
            print(f"duplicate: {entry.document_id} -> {duplicate.document_id}")

        entry.content_sha256 = sha256
        entry.file_size_bytes = size
        entry.updated_at = datetime.fromisoformat(_utc_now_iso().replace("Z", "+00:00"))
        updated += 1
        print(f"hashed: {entry.document_id} ({size} bytes)")

    if updated:
        save_catalog(entries)
        print(f"Updated {updated} entries in {DOCUMENTS_MANIFEST}")
    else:
        print("No manifest changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
