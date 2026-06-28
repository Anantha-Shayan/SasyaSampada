# 23 — Engineering Decisions (ADR Log)

Architecture Decision Records for SasyaSampada RAG. Phase 1 entries only; later phases append new ADRs.

---

## ADR-001: Layered backend inside monolithic FastAPI app

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1) |
| **Context** | Team size small; existing React + FastAPI app in production |
| **Decision** | Add RAG packages inside `backend/app/` rather than new microservice |
| **Alternatives** | Separate `rag-service`; LlamaIndex-only app |
| **Why not** | Ops overhead; loses shared auth/config; harder local dev |
| **Tradeoffs** | Simpler deploy; larger container image |
| **Consequences** | Clear package boundaries required to avoid spaghetti |

---

## ADR-002: Qdrant as vector database

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1, implement Phase 9) |
| **Context** | Need metadata filtering, persistence, Docker, hybrid search path |
| **Decision** | Qdrant with self-hosted Docker for dev |
| **Alternatives** | Pinecone, FAISS, Chroma, Endee |
| **Why not Pinecone** | Cost at scale; less control for on-prem rural deployments |
| **Why not FAISS** | No native payload filters; in-process only |
| **Why not Chroma** | Less mature ops story for production sharding |
| **Tradeoffs** | Operate another service; excellent filter + HNSW performance |

---

## ADR-003: bge-small-en-v1.5 default, bge-m3 optional

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1, implement Phase 8) |
| **Context** | Docs primarily English; multilingual user questions possible |
| **Decision** | `EMBEDDING_MODEL` env switches provider; default `bge-small-en-v1.5` (384-d) |
| **Alternatives** | OpenAI `text-embedding-3-small`; e5-large |
| **Why not OpenAI default** | Per-chunk API cost; offline requirement |
| **Tradeoffs** | Local CPU/GPU needed; bge-m3 slower but multilingual |

---

## ADR-004: Groq as default LLM provider

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1, implement Phase 12) |
| **Context** | Farmer chat needs low latency; `groq` already in requirements |
| **Decision** | `LLMProvider` protocol with Groq default; OpenRouter kept for legacy chat migration |
| **Alternatives** | OpenAI GPT-4; local Llama |
| **Why not GPT-4 default** | Cost per query for open advisory product |
| **Tradeoffs** | Groq model catalog limits; rate limits |

---

## ADR-005: Stage-separated ingestion pipeline

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1, implement Phase 3) |
| **Context** | PDF processing is multi-step with different failure modes |
| **Decision** | Protocol per stage + `IngestionPipeline` orchestrator |
| **Alternatives** | Monolithic script; LlamaIndex ingestion |
| **Why not monolith** | Cannot test chunker in isolation; cannot re-embed cheaply |
| **Tradeoffs** | More modules; clearer ops |

---

## ADR-006: Disk artifacts + Qdrant vectors (hybrid storage)

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1, detail Phase 2) |
| **Context** | Need replay, debug, re-embed without re-parse |
| **Decision** | Persist `parsed/`, `processed/`, `metadata/` on disk; vectors in Qdrant |
| **Alternatives** | Qdrant-only; filesystem-only |
| **Tradeoffs** | Disk usage; strong reproducibility |

---

## ADR-007: LangChain where appropriate only

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1) |
| **Context** | Requirements already include langchain, langchain-groq |
| **Decision** | Use LangChain for Groq LLM wrapper and optional text splitters; **not** as application framework |
| **Alternatives** | Full LangChain agent; zero LangChain |
| **Why not full LangChain** | Opaque chains fail interview depth; harder custom retrieval |
| **Tradeoffs** | Some dependency weight; faster Groq integration |

---

## ADR-008: Preserve existing ML and API routes during RAG build

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 1) |
| **Context** | Crop recommendation, weather, market already used by frontend |
| **Decision** | No breaking changes to `/api/advisory`, `/api/weather`, etc.; RAG under new `/api/v1/` prefix |
| **Alternatives** | Big-bang rewrite |
| **Tradeoffs** | Temporary dual chat endpoints until migration |

---

## ADR-009: Conventional commits per milestone

| Field | Content |
|-------|---------|
| **Status** | Accepted |
| **Context** | Professional Git history for code review |
| **Decision** | Atomic commits: `feat:`, `docs:`, `refactor:`, `test:`, `chore:` |
| **Tradeoffs** | Discipline required; easier bisect and review |

---

## ADR-010: Documentation as interview artifact

| Field | Content |
|-------|---------|
| **Status** | Accepted |
| **Context** | User requirement: defend every decision in Senior AI interview |
| **Decision** | All reasoning in `docs/` with 18-section template; code stays minimal-comment |
| **Tradeoffs** | Doc maintenance burden; high interview readiness |

---

## ADR-011: Manifest-driven document catalog

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 2) |
| **Context** | Need single source of truth for 6+ PDFs with lifecycle |
| **Decision** | `data/manifests/documents.json` validated by Pydantic + JSON Schema |
| **Alternatives** | SQLite catalog; YAML front matter in PDFs |
| **Why not** | JSON diffs well in PRs; no DB dependency for MVP |
| **Tradeoffs** | File-level locking at scale; shard later |

---

## ADR-012: Versioned artifact paths

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 2) |
| **Context** | Document updates must not destroy previous artifacts |
| **Decision** | `{document_id}/v{version}/` under parsed, processed, metadata, embeddings |
| **Alternatives** | Overwrite in place; timestamp paths |
| **Why not overwrite** | Cannot rollback or diff; breaks reproducibility |
| **Tradeoffs** | More directories; clear audit trail |

---

## ADR-013: Content-addressable deduplication

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 2) |
| **Context** | Same PDF may be uploaded under different names |
| **Decision** | `content_sha256` on raw file; `duplicate_of` points to canonical `document_id` |
| **Alternatives** | Filename-only dedup; perceptual hash |
| **Why not filename** | Copies and re-downloads collide |
| **Tradeoffs** | Must hash on every upload; negligible cost |

---

## ADR-014: IngestionPipeline orchestrator with Protocol-based stages

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 3) |
| **Context** | Need testable, swappable ingestion before Qdrant/embeddings exist |
| **Decision** | `IngestionPipeline` + eight Protocols + stub embed/vector stages |
| **Alternatives** | LangChain loaders; monolithic function |
| **Why not** | Opaque chains; cannot defend per-stage in interview |
| **Tradeoffs** | More modules; clear extension points for Phases 4–9 |

---

## ADR-015: Composite PDF parser (PyMuPDF + pdfplumber + optional OCR)

| Field | Content |
|-------|---------|
| **Status** | Accepted (Phase 4) |
| **Context** | Agri PDFs need tables, header/footer hints, scanned-page path |
| **Decision** | `CompositePdfParser` orchestrates PyMuPDF, pdfplumber, `OcrEngine` protocol |
| **Alternatives** | Unstructured; PyMuPDF-only; Textract |
| **Why not Unstructured** | Opaque; heavy; weak per-stage testing |
| **Tradeoffs** | Two PDF libs; optional Tesseract system dep |

---

## Template for future ADRs

```markdown
## ADR-NNN: Title
| Field | Content |
| **Status** | Proposed | Accepted | Deprecated |
| **Context** | ... |
| **Decision** | ... |
| **Alternatives** | ... |
| **Why not** | ... |
| **Tradeoffs** | ... |
| **Consequences** | ... |
```

## Interview pointer

When asked "Why did you choose X?" — cite ADR number and point to the dedicated doc (`docs/12_vector_database.md`, etc.) once written.

## References

- Document template sections defined in project requirements
- `docs/02_architecture.md`
