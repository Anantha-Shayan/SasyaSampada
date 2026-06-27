# `data/manifests/`

## Purpose

**Catalog and control plane** for the knowledge base. All lifecycle operations start here.

## Files

| File | Role |
|------|------|
| `documents.json` | Master catalog — one entry per logical document |
| `schema.json` | JSON Schema for catalog entries (validation) |
| `categories.json` | Allowed `category` values + descriptions |
| `ingestion_registry.json` | Append-only log of ingestion runs |
| `examples/` | Reference JSON shapes for pipeline stages |

## Lifecycle fields (per document)

| Field | Meaning |
|-------|---------|
| `ingestion_status` | Pipeline progress: `pending` → `indexed` / `failed` |
| `lifecycle_status` | `active`, `archived`, `deleted` |
| `version` | Integer; increment on content update |
| `content_sha256` | Dedup and change detection |
| `duplicate_of` | Points to canonical `document_id` if duplicate PDF |

## Operations

| Action | Manifest change |
|--------|-----------------|
| New upload | Append entry, `ingestion_status=pending` |
| Ingest success | `ingestion_status=indexed`, `indexed_at`, `chunk_count` |
| Content update | `version++`, reset pipeline fields, re-ingest |
| Soft delete | `lifecycle_status=deleted`, `deleted_at` |
| Dedup detected | `duplicate_of` set; skip Qdrant upsert |

Validate edits against `schema.json` before commit.
