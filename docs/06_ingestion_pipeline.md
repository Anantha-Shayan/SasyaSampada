# 06 — Ingestion Pipeline

## 1. Purpose

Document the **implemented** modular ingestion pipeline (`app/ingestion/`) that transforms cataloged PDFs into chunked metadata ready for embedding and vector indexing.

## 2. Problem Being Solved

Monolithic ingest scripts cannot be retried per stage, swapped for A/B tests (parser v1 vs v2), or unit-tested without running the full PDF→Qdrant path. Production pipelines need isolated stages with typed contracts.

## 3. Engineering Decision

**`IngestionPipeline` orchestrator** wires eight independent stages via Protocol interfaces:

```
Loader → Validator → Parser → Cleaner → Chunker → Metadata → Embedder → VectorStore
```

Each stage:
- Implements a Protocol in `ingestion/interfaces/base.py`
- Lives in `ingestion/stages/<name>.py`
- Logs via `core.logging` + per-run JSONL in `data/logs/`
- Raises typed exceptions from `core.exceptions`
- Embedder and vector store use `tenacity` retry (`ingestion/retry.py`)

**Phase 3 scope:** full pipeline wiring with **stub embedder** and **no-op vector store**. Parser/cleaner/chunker are minimal implementations enhanced in Phases 4–6.

## 4. Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| LangChain `DocumentLoader` chain | Black box; weak interview narrative |
| Single `ingest_pdf()` | No replay matrix |
| Prefect/Airflow now | Deferred to Phase 18 |
| Synchronous API ingest | Blocks workers; CLI first |

## 5. Why Alternative Was Not Selected

Explicit stages match ETL best practices, enable **mock-based pipeline tests**, and allow ops to re-run from any artifact checkpoint (see replay matrix below).

## 6. Tradeoffs

| Gain | Cost |
|------|------|
| Swappable stages via DI | More files than one script |
| Manifest status tracking | Extra disk writes per stage |
| Stub embed/vector unblocks pipeline test | Not production retrieval until Phases 8–9 |

## 7. Performance Implications

| Stage | Implementation | Dominant cost |
|-------|----------------|---------------|
| Loader | Read file + SHA-256 | Disk I/O |
| Validator | 8-byte header check | Negligible |
| Parser | PyMuPDF `get_text()` | CPU, scales with pages |
| Cleaner | String join | Negligible |
| Chunker | Fixed window | O(n) text |
| Metadata | JSONL write | Disk I/O |
| Embedder (stub) | Zero vectors | Negligible |
| Vector store (noop) | Log only | Negligible |

## 8. Scaling Considerations

- Pipeline is **CLI-invoked** today; Phase 13 adds API + background task; Phase 18 adds queue workers
- Per-document `run_id` enables parallel workers with document-level locking
- Stage artifacts on disk allow horizontal workers sharing NFS/S3

## 9. Production Considerations

- Manifest `ingestion_status` updated after each stage group
- Failed runs set `last_error` and append to `ingestion_registry.json`
- Duplicate documents (`duplicate_of`) short-circuit before loader
- Deleted documents (`lifecycle_status=deleted`) rejected

### Module map

| Path | Responsibility |
|------|----------------|
| `ingestion/interfaces/base.py` | Protocol definitions |
| `ingestion/stages/*.py` | Stage implementations |
| `ingestion/pipeline/runner.py` | `IngestionPipeline` |
| `ingestion/pipeline/context.py` | Context, result, manifest helpers |
| `ingestion/factory.py` | `build_default_pipeline()` |
| `ingestion/cli.py` | CLI entry point |
| `domain/schemas/ingestion.py` | Stage DTOs |
| `core/exceptions.py` | `IngestionError` hierarchy |
| `core/logging.py` | `IngestionLogWriter` |

### CLI

```bash
cd backend
python -m app.ingestion.cli ingest --document-id tnau_crop_production_guide_2020
python -m app.ingestion.cli ingest --all
```

## 10. Failure Cases

| Stage | Exception | Retry? |
|-------|-----------|--------|
| Loader | `LoaderError` | No |
| Validator | `NonRetryableError` | No |
| Parser | `ParserError` / `NonRetryableError` | No |
| Cleaner | `CleanerError` | No |
| Chunker | `ChunkerError` | No |
| Metadata | `MetadataError` | No |
| Embedder | `RetryableIngestionError` | Yes (Phase 8) |
| Vector store | `RetryableIngestionError` | Yes (Phase 9) |

## 11. Edge Cases

| Case | Behavior |
|------|----------|
| Missing raw PDF | `LoaderError`, manifest `failed` |
| PDF with no text | `NonRetryableError` at parser (OCR in Phase 4) |
| Duplicate catalog entry | Rejected before pipeline starts |
| Empty chunk list | `NonRetryableError` at chunker |

## 12. Security Concerns

- Validator checks `%PDF` magic bytes
- Filename must match manifest (path traversal prevention)
- 100 MB size cap in `PdfValidator`
- Logs exclude API keys and full chunk bodies in error paths

## 13. Cost Considerations

- Stub embedder avoids API cost during pipeline development
- Re-running pipeline reuses nothing until checkpoint resume (future); currently full re-run
- Incremental ingest via `content_sha256` at catalog level (Phase 2) — loader populates hash

## 14. Common Interview Questions

**Q: Why separate ingestion stages?**  
A: Single responsibility, isolated testing, different retry policies, replay from disk artifacts without re-parsing.

**Q: How do you swap the embedding model?**  
A: Inject a different `EmbeddingGenerator` implementation into `IngestionPipeline`; re-run from metadata stage.

**Q: What happens on failure?**  
A: Manifest `ingestion_status=failed`, `last_error` set, JSONL log records last completed stage, registry append.

## 15. Deep Interview Questions

**Q: How would you resume a failed run?**  
A: Read `stages_completed` from run log; add `start_from_stage` parameter to pipeline (future); load cached artifact from versioned path.

**Q: Why retry only embedder and vector store?**  
A: Network/rate-limit failures are transient; parse/validate failures are deterministic.

**Q: How test without PDFs?**  
A: Mock all stage protocols; see `tests/unit/test_ingestion_pipeline.py`.

## 16. Best Possible Answers

Walk the eight stages naming **input DTO → output DTO** and which file persists artifacts. Mention stub vs production implementations.

## 17. Diagrams

### Implemented stage chain

```
DocumentCatalogEntry (manifest)
        │
        ▼
┌─────────────────┐
│ FileSystemLoader │ → LoadedDocument
└────────┬────────┘
         ▼
┌─────────────────┐
│  PdfValidator   │ → ValidatedDocument
└────────┬────────┘
         ▼
┌─────────────────┐
│  PyMuPDFParser  │ → ParsedDocumentArtifact → data/parsed/.../parsed.json
└────────┬────────┘
         ▼
┌─────────────────┐
│AgriculturalTextCleaner│ → CleanedDocument → data/processed/.../cleaned.txt
└────────┬────────┘
         ▼
┌─────────────────────────┐
│RecursiveCharacterChunker│ → ChunkedDocument
└────────┬────────────────┘
         ▼
┌──────────────────────┐
│RichMetadataGenerator │ → MetadataBundle → data/metadata/.../chunks.jsonl
└────────┬─────────────┘
         ▼
┌──────────────────────┐
│StubEmbeddingGenerator │ → EmbeddedDocument (stub vectors)
└────────┬─────────────┘
         ▼
┌──────────────────────┐
│NoOpVectorStoreWriter │ → IndexedDocument (log only until Phase 9)
└──────────────────────┘
```

### Replay matrix

| Change | Re-run from stage |
|--------|-------------------|
| New embedding model | Embedder |
| Chunk size change | Chunker |
| Parser upgrade | Parser |
| New PDF | Loader (full pipeline) |

### Why pipelines are separated

1. **Testability** — mock one Protocol, test orchestrator
2. **Observability** — per-stage timing in JSONL logs
3. **Cost control** — skip embed when testing parse/clean
4. **Team velocity** — parser and infra engineers work in parallel
5. **Failure isolation** — know exactly which stage failed

## 18. References

- `backend/app/ingestion/pipeline/runner.py`
- `backend/app/ingestion/factory.py`
- `backend/app/domain/schemas/ingestion.py`
- `docs/knowledge_base_organization.md`
- `docs/23_engineering_decisions.md` (ADR-014)
