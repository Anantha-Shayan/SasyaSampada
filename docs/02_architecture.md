# 02 — System Architecture

## 1. Purpose

Describe the target production architecture, repository layout, component boundaries, and how existing code coexists with the new RAG subsystem.

## 2. Problem Being Solved

The pre-RAG codebase grew organically: multiple deleted `main_*.py` entry points were consolidated, but there is no clear boundary between HTTP, ingestion, retrieval, and generation. Without a defined architecture, RAG logic would leak into route handlers and become untestable.

## 3. Engineering Decision

Adopt a **layered, ports-and-adapters** layout inside `backend/app/`:

```
Presentation  →  api/v1/endpoints/
Application   →  rag/, services/
Domain        →  domain/schemas/
Infrastructure→  ingestion/, retrieval/, embeddings/, vector_db/, llm/
Cross-cutting →  core/
```

**Data plane** lives under `data/` with stage-specific subdirectories (detailed in Phase 2).

## 4. Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Single `rag/` package with everything | Too coarse; ingestion and query have different scaling profiles |
| LlamaIndex as the application framework | Heavy abstraction; harder to defend design choices |
| NestJS-style modules per feature | Overkill for Python FastAPI |
| Monorepo with separate `rag-service/` repo | Premature split |

## 5. Why Alternative Was Not Selected

Ports-and-adapters keeps **interfaces testable** (mock `VectorStore` in unit tests) and matches how Staff engineers evaluate system design: clear boundaries, explicit data contracts, swappable infrastructure.

## 6. Tradeoffs

| Advantage | Disadvantage |
|-----------|--------------|
| Each layer independently testable | More packages than a 200-line script |
| Swappable Qdrant/Groq/embeddings | Initial scaffolding without behavior (Phase 1) |
| Existing routes untouched | Temporary duplication (`models/` vs `domain/schemas/`) |

## 7. Performance Implications

- Ingestion and query paths are **decoupled** — bulk embed jobs do not block API workers
- Async FastAPI endpoints (Phase 13) for I/O-bound LLM and Qdrant calls
- Embedding batching in ingestion; single-vector query embed at retrieval time

## 8. Scaling Considerations

See `docs/16_scalability.md`. Summary: horizontal API replicas, dedicated Qdrant cluster, optional embedding service, async ingestion queue (Kafka, Phase 18).

## 9. Production Considerations

- Health checks cover API + Qdrant + embedding model load status
- Configuration via `core.config` pydantic-settings (Phase 15)
- Docker Compose adds `qdrant` service (Phase 17)

## 10. Failure Cases

- Misplaced business logic in `api/` → prevented by README conventions in each package
- Circular imports between `rag` and `ingestion` → `rag` depends on `retrieval`, not `ingestion`

## 11. Edge Cases

- ML inference remains in `app/ml/` — not merged into RAG to avoid loading sklearn and sentence-transformers in the same process unnecessarily (configurable later)

## 12. Security Concerns

- `api/` is the only internet-facing layer; internal packages never parse raw HTTP
- Upload size limits enforced at API before touching `data/raw/`

## 13. Cost Considerations

- Modular embedding provider allows switching from local CPU to API under cost/latency tradeoffs without changing chunker or API code

## 14. Common Interview Questions

**Q: Draw the high-level architecture.**  
A: See diagram below — Client → FastAPI → RAG Service → (Retriever → Qdrant, LLM → Groq); parallel path for ML advisory.

**Q: Why separate `retrieval` from `rag`?**  
A: Retrieval is reusable for `/search` without LLM cost; RAG adds prompting and citation.

## 15. Deep Interview Questions

**Q: How does this map to CLEAN/hexagonal architecture?**  
A: `domain/schemas` = entities/DTOs; `ingestion/interfaces` = ports; `vector_db/qdrant` = adapter; `api` = driving adapter.

**Q: Where does LangChain fit?**  
A: Optional thin wrappers in `llm/providers` and `embeddings/providers` only where it reduces boilerplate — not as the application skeleton.

## 16. Best Possible Answers

Walk through the folder tree verbally, naming one responsibility per package. Emphasize **dependency direction**: `api → rag → retrieval → vector_db`; `ingestion → vector_db`; never `vector_db → api`.

## 17. Diagrams

### Component diagram

```
                    ┌──────────────┐
                    │   Frontend   │
                    │   (React)    │
                    └──────┬───────┘
                           │ HTTP
                    ┌──────▼───────┐
                    │  api/v1/     │
                    │  endpoints   │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  services/  │ │   rag/      │ │ ingestion/  │
    │  ml, weather│ │             │ │  pipeline   │
    └─────────────┘ └──────┬──────┘ └──────┬──────┘
                           │               │
                    ┌──────▼──────┐ ┌──────▼──────┐
                    │ retrieval/  │ │ embeddings/ │
                    └──────┬──────┘ └──────┬──────┘
                           │               │
                    ┌──────▼───────────────▼──────┐
                    │      vector_db/qdrant       │
                    └─────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Qdrant    │
                    │  (Docker)   │
                    └─────────────┘
```

### Repository folder structure

```text
SasyaSampada/
├── docs/                          # Architecture & interview documentation
├── data/
│   ├── raw/                       # Source PDFs (immutable inputs)
│   ├── processed/                 # Post-cleaning artifacts
│   ├── parsed/                    # Structured parse output (JSON)
│   ├── metadata/                  # Per-document & per-chunk metadata
│   ├── embeddings/                # Optional embedding cache/export
│   ├── logs/                      # Ingestion pipeline logs
│   ├── manifests/                 # documents.json catalog
│   └── datasets/                  # Tabular ML data (mandi, ICRISAT)
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry
│   │   ├── api/
│   │   │   ├── routes.py          # Legacy routes (active)
│   │   │   └── v1/endpoints/      # Future route modules
│   │   ├── core/                  # Config, logging, DI, exceptions
│   │   ├── domain/schemas/        # Pydantic models (target home)
│   │   ├── models/                # Current schemas (migration pending)
│   │   ├── ingestion/
│   │   │   ├── interfaces/        # Stage protocols
│   │   │   ├── stages/            # Implementations
│   │   │   └── pipeline/          # Orchestrator
│   │   ├── embeddings/providers/
│   │   ├── vector_db/qdrant/
│   │   ├── retrieval/
│   │   ├── rag/
│   │   ├── llm/providers/
│   │   ├── services/              # Weather, market, legacy chat
│   │   └── ml/                    # Crop recommendation inference
│   ├── model_assets/              # Pickled ML models
│   └── tests/
│       ├── unit/
│       └── integration/
├── frontend/                      # React SPA
├── training/                      # Offline ML training scripts
├── scripts/                       # Dev/ops helpers
└── docker-compose.yml
```

### Folder responsibilities

| Path | Responsibility |
|------|----------------|
| `docs/` | All design decisions, flows, tradeoffs — single source of truth for interviews |
| `data/raw/` | Immutable PDF sources; never overwritten in place |
| `data/manifests/` | Canonical document catalog with ids, versions, categories |
| `app/api/` | HTTP translation only; no embedding or parsing |
| `app/core/` | Settings, logging, shared exceptions, FastAPI Depends() factories |
| `app/ingestion/` | Offline document processing pipeline |
| `app/retrieval/` | Online similarity search and ranking |
| `app/rag/` | Query orchestration, prompts, citations |
| `app/embeddings/` | Model-agnostic vectorization |
| `app/vector_db/` | Persistence and search backend |
| `app/llm/` | Text generation providers |
| `app/services/` | Non-RAG integrations (weather, market, legacy chat) |
| `app/ml/` | Structured crop recommendation — orthogonal to RAG |
| `training/` | Not imported at runtime; keeps ML training out of API memory |

## 18. References

- Martin Fowler, "Hexagonal Architecture"
- FastAPI project structure best practices
- Package README files under `backend/app/*/README.md`
