# 04 — Data Flow

## 1. Purpose

Describe how agricultural knowledge **enters**, **transforms**, **indexes**, and **exits** the system — the full data lifecycle from PDF bytes to cited LLM answers.

## 2. Problem Being Solved

RAG failures often stem from unclear data lineage: stale chunks, wrong metadata, or embeddings computed on dirty text. Explicit stage directories and schemas make every artifact inspectable and replayable.

## 3. Engineering Decision

**Dual pipeline model:**

- **Ingestion flow (write path):** raw → parsed → cleaned → chunked → embedded → Qdrant + metadata files
- **Query flow (read path):** question → query embedding → Qdrant search → context assembly → LLM → response

Artifacts persist on disk under `data/` **and** vectors in Qdrant. Disk is source of truth for replay; Qdrant is optimized read path.

## 4. Alternatives Considered

| Alternative | Issue |
|-------------|-------|
| Qdrant-only storage (no disk artifacts) | Cannot re-embed without re-parsing PDFs |
| Disk-only (no vector DB) | Linear scan; no metadata filters at scale |
| Stream-only (Kafka) without persistence | Harder to debug for MVP |

## 5. Why Alternative Was Not Selected

Hybrid disk + Qdrant supports **incremental re-indexing** (re-embed all chunks when swapping bge-small → bge-m3) without re-parsing, while Qdrant provides sub-100ms search.

## 6. Tradeoffs

| Gain | Pain |
|------|------|
| Reproducible pipeline stages | Disk usage grows with corpus |
| Debuggable JSON intermediates | Must keep manifest in sync with Qdrant |

## 7. Performance Implications

- Ingestion: dominated by PDF parse + embed batch size
- Query: single query vector + top-K HNSW search
- Metadata JSON on disk: read only during admin/reindex — not on hot path

## 8. Scaling Considerations

- Partition Qdrant collections by `category` or year if payload grows large
- Move `data/raw/` to S3/GCS; loader abstracts storage backend
- Embedding cache in `data/embeddings/` keyed by content hash

## 9. Production Considerations

- Content-addressable chunk hashes detect unchanged chunks on re-ingest
- Manifest `documents.json` is authoritative catalog (Phase 2)
- Ingestion logs in `data/logs/{document_id}/{run_id}.jsonl`

## 10. Failure Cases

| Failure | Data state |
|---------|--------------|
| Embed succeeds, Qdrant upsert fails | Retry upsert; disk embeddings intact |
| Partial chunk write | Transactional batch upsert per document |
| Manifest out of sync | Reconciliation job compares manifest vs. Qdrant point count |

## 11. Edge Cases

- Document update: new `version` in manifest → delete old Qdrant points by `document_id` filter → re-ingest
- Duplicate content hash, different filename → dedupe at validation stage (Phase 2)

## 12. Security Concerns

- Raw PDFs may contain embedded JavaScript — parse with safe libraries only
- Logs must not contain API keys or full farmer chat PII

## 13. Cost Considerations

- Storing parsed JSON ~2–5× PDF size — acceptable for 6 docs; compress with gzip at scale
- Re-embedding only changed chunks saves GPU time

## 14. Common Interview Questions

**Q: What data stores do you use?**  
A: Filesystem stages under `data/`, Qdrant for vectors+payload, manifest JSON for catalog.

**Q: What is stored in Qdrant payload vs. vector?**  
A: Vector = embedding; payload = chunk text snippet + metadata (document_id, page, title) for filtering and citation.

## 15. Deep Interview Questions

**Q: How do you handle document deletion?**  
A: Delete Qdrant points where `document_id=X`; remove/raw/archive files; update manifest status to `deleted`.

**Q: Eventual consistency between disk and Qdrant?**  
A: Ingestion pipeline treats Qdrant upsert as final commit step; status field in manifest: `processing|indexed|failed`.

## 16. Best Possible Answers

Draw two arrows — write path and read path — and name the artifact at each stage with its schema (`ParsedDocument`, `DocumentChunk` in `schemas.py`).

## 17. Diagrams

### Write path (ingestion)

```
PDF file
   │
   ▼
data/raw/{filename}.pdf
   │
   ▼  Loader + Validator
   │
   ▼  Parser (PyMuPDF / pdfplumber)
data/parsed/{document_id}.json
   │
   ▼  Cleaner
data/processed/{document_id}.txt
   │
   ▼  Chunker
chunks[] (in memory)
   │
   ▼  Metadata Generator
data/metadata/{document_id}/chunks.jsonl
   │
   ▼  Embedding Generator
vectors[] (+ optional data/embeddings/{document_id}.npy)
   │
   ▼  VectorStoreWriter
Qdrant collection "agri_knowledge"
   │
   ▼
manifest: status = "indexed"
```

### Read path (query)

```
User question (string)
   │
   ▼
Query embedding (same model as ingestion)
   │
   ▼
Qdrant similarity search (top-K, optional filters)
   │
   ▼
RetrievedChunk[] (text + metadata + score)
   │
   ▼
Context string (ranked, truncated to token budget)
   │
   ▼
LLM prompt
   │
   ▼
Answer + citations
```

### Data types (existing Pydantic seeds)

| Model | Stage | Location |
|-------|-------|----------|
| `DocumentMetadata` | catalog | manifest + chunk payload |
| `ParsedDocument` | post-parse | `data/parsed/` |
| `CleanDocument` | post-clean | `data/processed/` |
| `DocumentChunk` | post-chunk | metadata JSONL |

## 18. References

- `backend/app/models/schemas.py`
- `data/manifests/documents.json`
- `docs/06_ingestion_pipeline.md`
- `docs/05_rag_pipeline.md`
