# Knowledge Base Organization

## 1. Purpose

Define how agricultural documents **live on disk**, how they are **cataloged**, **versioned**, **deduplicated**, **updated**, **deleted**, and **incrementally ingested** — the data foundation for the entire RAG system.

## 2. Problem Being Solved

Without a canonical layout, teams store PDFs ad hoc, lose track of which chunks belong to which policy revision, double-index duplicates, and cannot re-embed after a model change without re-parsing everything. Production RAG requires **inspectable lineage** from `raw/` bytes to Qdrant point ids.

## 3. Engineering Decision

**Manifest-driven, versioned artifact tree** under `data/`:

| Directory | Stage output |
|-----------|--------------|
| `raw/` | Original PDF (immutable) |
| `parsed/` | Structured JSON per page |
| `processed/` | Cleaned plain text |
| `metadata/` | Chunk JSONL + document aggregates |
| `embeddings/` | Optional vector cache per model |
| `logs/` | Per-run audit JSONL |
| `manifests/` | Catalog, schema, registry |

**Control plane:** `manifests/documents.json` — every lifecycle operation updates this file first.

**Code:** `app/knowledge_base/` — path resolution (`paths.py`) and catalog I/O (`registry.py`).

## 4. Alternatives Considered

| Alternative | Issue |
|-------------|-------|
| Flat `data/docs/*.pdf` only | No stage artifacts; cannot replay pipeline |
| Database as sole metadata store | Harder to debug; couples ops to DB uptime |
| Git LFS for all artifacts | Massive repo; wrong tool for generated JSON |
| Single `chunks.json` per corpus | Lock contention; no per-document incremental ingest |
| Content in Qdrant payload only | Re-index requires re-parse on model swap |

## 5. Why Alternative Was Not Selected

Filesystem stages are **gitignorable**, **human-inspectable**, and **replayable**. Manifest JSON is small enough to commit and code-review. Qdrant remains a derived index rebuildable from `metadata/` + embeddings cache.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Clear debugging (`cat chunks.jsonl`) | Disk growth ~3–8× raw PDF size |
| Per-document incremental ingest | Path discipline enforced by convention |
| Version rollback (keep `v1/` while building `v2/`) | Must reconcile manifest ↔ Qdrant |

## 7. Performance Implications

- Hot query path reads **Qdrant only** — disk metadata not touched
- Incremental ingest skips unchanged stages via `content_sha256` and per-chunk `content_hash`
- JSONL chunk files stream to embedder without loading full doc in memory
- Embedding cache avoids recomputing vectors on Qdrant upsert retry

## 8. Scaling Considerations

| Scale | Change |
|-------|--------|
| 10² docs | Current layout |
| 10⁴ docs | `raw/` → S3; manifest shards by category prefix |
| 10⁶ docs | Per-category Qdrant collections; compaction job for old versions |
| High churn | Kafka `document.updated` events; worker pool with per-id locks |

## 9. Production Considerations

- **Immutability:** never overwrite `raw/` bytes; bump `version`
- **Idempotency:** chunk_id deterministic from `document_id + version + index`
- **Validation:** Pydantic `DocumentCatalogEntry` + JSON Schema on CI
- **Reconciliation:** nightly job compares `chunk_count` vs Qdrant point count per `document_id`
- **Backup:** manifest + raw PDFs to object storage; Qdrant snapshots separately
- **Script:** `scripts/hash_raw_documents.py` populates `content_sha256` from `data/raw/`

## 10. Failure Cases

| Failure | Recovery |
|---------|----------|
| Ingest crash mid-pipeline | `ingestion_status=failed`, `last_error` set; replay from last completed stage |
| Manifest save corrupt | Restore from git; re-run reconciliation |
| Duplicate upload same hash | `duplicate_of` set; skip Qdrant upsert |
| Delete API called | Soft delete manifest; async Qdrant delete by filter |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Same title, different years | Distinct `document_id` (includes year slug) |
| Revised PDF same `document_id` | `version++`, new versioned paths, delete old Qdrant points |
| Partial OCR document | `ocr_applied` per page in `parsed.json`; chunk metadata flags low confidence |
| Zero-byte upload | Validation rejects before manifest append |
| Farmer uploads non-agri PDF | Category + manual review hook (future) |

## 12. Security Concerns

- Sanitize filenames (no `..`, no absolute paths)
- Raw PDFs may be malicious — parse with hardened libraries; no auto-execute
- Manifest edits via API require auth (Phase 13)
- Logs must not store full chunk text if it contains PII

## 13. Cost Considerations

- Gitignore generated artifacts — S3 lifecycle rules move `v{n-1}/` to cold storage
- Dedup by SHA-256 avoids duplicate embedding charges
- Re-embed only when model changes — reuse `metadata/chunks.jsonl`

## 14. Common Interview Questions

**Q: Why separate `raw`, `parsed`, `processed`, `metadata`?**  
A: Each maps to an ingestion stage; failures can retry from the last artifact; stages have different sizes and regeneration costs.

**Q: What is the source of truth?**  
A: `manifests/documents.json` for catalog; `metadata/chunks.jsonl` for chunk text; Qdrant is derived.

**Q: How do chunk IDs work?**  
A: `{document_id}::v{version}::chunk_{index:04d}` — stable, filterable, used as Qdrant point id.

## 15. Deep Interview Questions

**Q: Document updates every minute — what breaks?**  
A: Per-minute full re-ingest is too heavy; use content hash diff → re-chunk only changed pages → upsert delta points → delete stale point ids. Queue-backed workers with debounce.

**Q: How handle duplicate documents?**  
A: SHA-256 on upload; if match exists, set `duplicate_of` to canonical entry; retrieval always resolves to canonical chunks.

**Q: Soft vs hard delete?**  
A: Soft: `lifecycle_status=deleted`, hide from API, delete Qdrant points. Hard: remove raw + artifacts after retention period.

## 16. Best Possible Answers

Explain **three axes**: (1) pipeline stage directories, (2) manifest lifecycle fields, (3) versioned paths. Walk through update and dedup flows with concrete field names.

## 17. Diagrams

### Directory responsibilities

```
raw/          ──► immutable source PDF
  │
  ▼ parse
parsed/       ──► structured pages (JSON)
  │
  ▼ clean
processed/    ──► normalized text
  │
  ▼ chunk + enrich
metadata/     ──► chunks.jsonl (retrieval payload source)
  │
  ▼ embed
embeddings/   ──► optional vector cache
  │
  ▼ upsert
Qdrant        ──► search index (derived)

logs/         ──► audit every run (orthogonal)
manifests/    ──► catalog ties it all together
```

### Versioning flow

```
Upload revised PMFBY PDF
        │
        ▼
manifest.version: 1 → 2
ingestion_status: indexed → pending
        │
        ▼
Write raw (new file or archived copy)
        │
        ▼
Create paths: .../v2/parsed.json, etc.
        │
        ▼
On index complete:
  - DELETE Qdrant points WHERE document_id=X AND version<2
  - indexed_at = now, chunk_count = N
```

### Incremental ingestion decision tree

```
New file uploaded
        │
        ▼
Compute SHA-256
        │
   ┌────┴────┐
   │         │
 match?    no match
   │         │
   ▼         ▼
duplicate_of  New manifest entry
set           version=1
skip embed    full pipeline
```

### Deletion flow

```
DELETE /documents/{id}
        │
        ▼
lifecycle_status = deleted
deleted_at = now
        │
        ▼
Async: Qdrant delete by document_id filter
        │
        ▼
Optional: move raw → raw/_archived/
(Do NOT delete logs — audit retention)
```

### Manifest field reference

| Field | Role |
|-------|------|
| `ingestion_status` | Pipeline progress |
| `lifecycle_status` | active / archived / deleted |
| `version` | Content revision integer |
| `content_sha256` | Whole-file dedup & change detect |
| `duplicate_of` | Canonical doc if duplicate |
| `chunk_count` | Reconciliation with Qdrant |
| `embedding_model` | Which model indexed this version |

## 18. References

- [`data/README.md`](../data/README.md)
- [`data/manifests/schema.json`](../data/manifests/schema.json)
- [`app/knowledge_base/paths.py`](../backend/app/knowledge_base/paths.py)
- [`app/domain/schemas/knowledge_base.py`](../backend/app/domain/schemas/knowledge_base.py)
- `docs/04_data_flow.md`
- `docs/06_ingestion_pipeline.md`
