# Knowledge Base — `data/`

Canonical on-disk layout for the SasyaSampada agricultural RAG knowledge base.

## Directory map

| Path | Role | Mutable | Git |
|------|------|---------|-----|
| `raw/` | Original PDF uploads — **immutable** after ingest | Append-only | PDFs committed or S3 |
| `parsed/` | Structured parser output (JSON per page) | Per version | Ignored (except examples) |
| `processed/` | Cleaned plain text after noise removal | Per version | Ignored |
| `metadata/` | Chunk records + enrichment (JSONL) | Per version | Ignored |
| `embeddings/` | Optional vector cache / export | Per version | Ignored |
| `logs/` | Ingestion run audit trail | Append | Ignored |
| `manifests/` | Catalog, schema, registry — **source of truth** | Updated on lifecycle events | Committed |
| `datasets/` | Tabular ML data (mandi, ICRISAT) — **not RAG** | Training only | Committed |

## Golden rules

1. **`manifests/documents.json` is authoritative** for what exists in the knowledge base.
2. **Never overwrite** `raw/{filename}` in place — bump `version` and write to versioned artifact paths.
3. **Qdrant is a derived index** — rebuildable from `metadata/` + `embeddings/` + manifest.
4. **`document_id` is stable** — survives filename changes; use manifest to resolve paths.
5. **Chunk identity** = `{document_id}::v{version}::chunk_{index:04d}` — used in Qdrant point IDs.

## Versioned artifact layout

```text
data/
├── raw/
│   └── {filename}.pdf
├── parsed/
│   └── {document_id}/
│       └── v{version}/
│           └── parsed.json
├── processed/
│   └── {document_id}/
│       └── v{version}/
│           └── cleaned.txt
├── metadata/
│   └── {document_id}/
│       └── v{version}/
│           ├── chunks.jsonl
│           └── document_meta.json
├── embeddings/
│   └── {document_id}/
│       └── v{version}/
│           └── {embedding_model_slug}/
│               ├── manifest.json
│               └── vectors.npy
└── logs/
    └── {document_id}/
        └── {run_id}.jsonl
```

## Quick links

- Catalog schema: [`manifests/schema.json`](manifests/schema.json)
- Category taxonomy: [`manifests/categories.json`](manifests/categories.json)
- Run history: [`manifests/ingestion_registry.json`](manifests/ingestion_registry.json)
- Examples: [`manifests/examples/`](manifests/examples/)
- Full design doc: [`../docs/knowledge_base_organization.md`](../docs/knowledge_base_organization.md)
