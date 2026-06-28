# 10 — Metadata

## 1. Purpose

Document how **rich chunk-level metadata** is generated, persisted, and used for filtered retrieval, citations, and future domain extensions.

## 2. Problem Being Solved

Vector search alone returns semantically similar but contextually wrong chunks (e.g., wheat advice when filtering for `crop_insurance`). Without structured metadata, the system cannot cite page numbers, section titles, or filter by document category — critical for farmer trust and PMFBY policy questions.

## 3. Engineering Decision

**`RichMetadataGenerator`** (`app/ingestion/stages/metadata/`) produces:

- Per-chunk `ChunkRecord` JSONL at `data/metadata/{id}/v{n}/chunks.jsonl`
- Document envelope at `document_meta.json` with `schema_version` and `ext.future_fields`

| Field | Source |
|-------|--------|
| `document_id` | Catalog + chunk id factory |
| `chunk_id` | `{document_id}::v{version}::chunk_{index:04d}` |
| `chunk_index` / `total_chunks` | Chunker |
| `filename` | Catalog |
| `page_start` / `page_end` | Page mapper + parsed artifact |
| `section_title` | Section detector heuristics |
| `source`, `language`, `category` | Catalog |
| `title`, `organization`, `year` | Catalog |
| `created_at`, `ingested_at` | Ingestion timestamp |
| `content_hash` | SHA-256 of chunk text |
| `chunker_name` | ChunkedDocument |
| `token_count` | Word-count estimate |

## 4. Alternatives Considered

| Alternative | Issue |
|-------------|-------|
| Metadata only in Qdrant payload | No disk replay; harder to audit |
| LLM-generated metadata | Non-deterministic; costly |
| Filename-only citations | Insufficient for multi-hundred-page PDFs |
| Embed metadata in chunk text | Pollutes embeddings; duplicates boilerplate |

## 5. Why Alternative Was Not Selected

Structured JSONL metadata is **inspectable**, **versioned** (`metadata_schema_version`), and **filterable** in Qdrant without re-parsing PDFs. Heuristic section/page inference is good enough for MVP; extensibility hook allows ML enrichers later.

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Metadata-filtered retrieval | Heuristic page/section may be imperfect |
| Citation-ready payloads | Larger JSONL per chunk |
| Schema versioning | Migration work when schema bumps |

## 7. Performance Implications

- Page mapping loads cached `parsed.json` — O(pages × chunks) substring checks; acceptable for 6 docs
- Section detection is regex on chunk start — negligible
- Metadata stage does not call LLM or embedder

## 8. Scaling Considerations

- Precompute page offsets in chunker (future) to avoid substring scans
- Shard `ext` fields per domain (geo, season) without breaking schema v1
- Index only filterable fields in Qdrant payload — not full chunk text twice

## 9. Production Considerations

- `metadata_schema_version = "1.0"` on every record
- `document_meta.ext.future_fields` documents planned enrichments
- `DefaultMetadataGenerator` alias preserves backward compatibility
- Idempotent: re-run overwrites JSONL for document version

### Future extensibility (`document_meta.ext`)

```json
{
  "future_fields": [
    "crop_type", "season", "state", "district",
    "confidence_score", "ocr_applied"
  ]
}
```

Add enrichers as new modules implementing `MetadataEnricher` protocol (Phase 18).

## 10. Failure Cases

| Case | Behavior |
|------|----------|
| No parsed.json | Page fields null; chunk still indexed |
| No heading in chunk | `section_title` null |
| Duplicate chunk hash | Same `content_hash`; upsert idempotency in Phase 9 |

## 11. Edge Cases

| Case | Handling |
|------|----------|
| Chunk spans pages | `page_start` < `page_end` when probe matches multiple |
| Table chunk | `section_title` = `Table N` |
| Non-English docs | Section patterns English-biased; extend regex per language |

## 12. Security Concerns

- Metadata mirrors catalog — no user PII
- `source_url` validated at catalog level

## 13. Cost Considerations

- Zero API cost — all heuristics local

## 14. Common Interview Questions

**Q: Why metadata matters in RAG?**  
A: Enables filtered search, citations, dedup, debugging, and trust — not just semantic similarity.

**Q: Why store metadata on disk and in Qdrant?**  
A: Disk is source of truth for replay; Qdrant payload enables query-time filters.

## 15. Deep Interview Questions

**Q: How cite a chunk in the LLM answer?**  
A: Use `filename`, `page_start`, `section_title`, `source` from retrieved `ChunkRecord` payload.

**Q: How evolve schema without re-ingesting everything?**  
A: Bump `metadata_schema_version`; migration job reads JSONL, adds fields, optional re-embed only if text changed.

## 16. Best Possible Answers

List all chunk fields, explain page mapper + section detector, and point to `ext.future_fields` for crop/season/geo enrichment.

## 17. Diagrams

```
ChunkedDocument + DocumentCatalogEntry
              │
              ▼
     Load parsed.json (optional)
              │
              ▼
   For each chunk:
     ├── map_chunk_to_pages()
     ├── detect_section_title()
     ├── make_chunk_id()
     └── build ChunkRecord
              │
              ▼
   chunks.jsonl + document_meta.json
              │
              ▼
   Qdrant payload (Phase 9)
```

## 18. References

- `backend/app/ingestion/stages/metadata/generator.py`
- `data/manifests/examples/chunk_record.example.json`
- `docs/knowledge_base_organization.md`
- `docs/13_retrieval.md`
