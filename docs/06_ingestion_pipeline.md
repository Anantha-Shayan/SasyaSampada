# 06 — Ingestion Pipeline (Architecture)

## 1. Purpose

Define the **offline write path** that transforms PDFs into searchable vectors. Blueprint for `app/ingestion/` (Phases 3–9).

## 2. Problem Being Solved

Agricultural PDFs are long, noisy (headers, page numbers, tables), and heterogeneous (text vs. scanned). A single monolithic script cannot be retried, tested, or swapped per stage.

## 3. Engineering Decision

**Independent stages** connected by a thin orchestrator (`IngestionPipeline`), each implementing a Protocol in `ingestion/interfaces/`:

```
Loader → Validation → Parser → Cleaner → Chunker → Metadata → Embedding → Vector DB
```

Each stage:
- Accepts a typed input DTO
- Returns a typed output DTO
- Logs start/end/duration
- Retries transient failures (`tenacity`)
- Raises domain exceptions (`core.exceptions`)

## 4. Alternatives Considered

| Alternative | Issue |
|-------------|-------|
| One `ingest_pdf()` function | Cannot unit test chunker without parsing |
| Airflow/Prefect DAG on day one | Ops overhead for 6 PDFs |
| LlamaIndex `SimpleDirectoryReader` | Black-box parsing; weak PDF table handling |
| Celery task per stage | Good at scale; defer to Phase 18 |

## 5. Why Alternative Was Not Selected

Stage separation matches **ETL best practices** and interview expectations: "How would you re-run embedding without re-parsing?" → run stages 7–8 only from disk artifacts.

## 6. Tradeoffs

| Advantage | Cost |
|-----------|------|
| Stage-level unit tests | Serialization between stages |
| Partial pipeline replay | More files on disk |
| Team parallelization (parser vs. embed) | Interface design upfront |

## 7. Performance Implications

- Parser is CPU-bound (PyMuPDF) — dominant for large PDFs
- Embedding batched (32–64 chunks) for GPU utilization
- Qdrant upsert batched (100–500 points)

## 8. Scaling Considerations

- Async ingestion queue when upload rate exceeds single-worker throughput
- Horizontal workers with document-level locking via `document_id`
- OCR stage optional branch for scanned pages only

## 9. Production Considerations

- Idempotent runs: same `document_id` + `content_hash` skips unchanged work
- Dead letter: manifest `status=failed` + `data/logs/` stack trace
- CLI: `python -m app.ingestion.cli ingest --document-id X` for ops

## 10. Failure Cases

| Stage | Failure | Action |
|-------|---------|--------|
| Validation | Not a PDF / too large | Reject; no partial writes |
| Parser | Encrypted PDF | Log; mark failed |
| Embed | OOM | Reduce batch size; retry |
| Qdrant | Connection refused | Retry 3x; exponential backoff |

## 11. Edge Cases

- Zero-text page (image only) → OCR branch flag in parsed JSON
- Table extracted as gibberish → pdfplumber table path (Phase 4)
- Empty document after clean → fail before embed

## 12. Security Concerns

- Validate magic bytes `%PDF` not just extension
- Sandboxed parsing — no `eval` on PDF metadata
- Path traversal prevention on uploaded filenames

## 13. Cost Considerations

- Re-embed only when `EMBEDDING_MODEL` changes — reuse parsed/cleaned artifacts
- Local embedding avoids per-token API fees for 10⁵+ chunks at scale

## 14. Common Interview Questions

**Q: Why separate ingestion from the API?**  
A: Different scaling profile, long-running work, retry semantics, and keeps request workers responsive.

**Q: What is the ingestion input/output?**  
A: Input: PDF path + manifest entry. Output: N points in Qdrant + metadata JSONL on disk.

## 15. Deep Interview Questions

**Q: How do you incrementally ingest new documents?**  
A: Add manifest entry → run pipeline for that `document_id` only → upsert new points without touching others.

**Q: How do you update an existing document?**  
A: Bump version → delete points with old `document_id`+`version` filter → full pipeline re-run.

## 16. Best Possible Answers

Explain **why pipelines are separated**: single responsibility, isolated testing, replay from checkpoints, different retry policies per stage (network for Qdrant, CPU for parse).

## 17. Diagrams

### Stage chain

```
┌────────┐   ┌────────────┐   ┌────────┐   ┌─────────┐
│ Loader │──▶│ Validation │──▶│ Parser │──▶│ Cleaner │
└────────┘   └────────────┘   └────────┘   └────┬────┘
                                                  │
    ┌─────────┐   ┌──────────┐   ┌───────────┐     │
    │ Qdrant  │◀──│ Embedding│◀──│ Metadata  │◀────┤
    │ Upsert  │   │ Generator│   │ Generator │◀───┤
    └─────────┘   └──────────┘   └───────────┘     │
                                          ┌─────────┴────────┐
                                          │    Chunker     │
                                          └────────────────┘
```

### Retrieval flow (read path summary)

Ingestion **writes** the index that retrieval **reads**:

```
Ingestion:  chunk text ──embed──▶ vector ──upsert──▶ Qdrant
Retrieval:  query ──embed──▶ vector ──search──▶ top-K chunks
```

See `docs/04_data_flow.md` for full read/write diagrams.

### Stage interfaces (planned)

```python
# Conceptual — implementation Phase 3
class DocumentParser(Protocol):
    def parse(self, source: ValidatedDocument) -> ParsedDocument: ...

class DocumentChunker(Protocol):
    def chunk(self, doc: CleanDocument) -> list[Chunk]: ...
```

### Why separation matters — replay matrix

| Change | Re-run from |
|--------|-------------|
| New embedding model | Embedding → Qdrant |
| Chunk size tweak | Chunker → end |
| Parser bug fix | Parser → end |
| New PDF | Full pipeline |

## 18. References

- `app/ingestion/interfaces/README.md`
- `app/ingestion/stages/README.md`
- `backend/app/models/schemas.py` (DTO seeds)
- `app/ingestion/parser.py` (temporary scratch — replace Phase 4)
