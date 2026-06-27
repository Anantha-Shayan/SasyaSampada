# 03 — Request Flow

## 1. Purpose

Document how HTTP requests traverse the system for both **existing endpoints** (today) and **planned RAG endpoints** (Phase 13).

## 2. Problem Being Solved

Without a defined request lifecycle, middleware concerns (CORS, logging, auth) get duplicated; error shapes become inconsistent; latency cannot be attributed to retrieval vs. LLM.

## 3. Engineering Decision

**Uniform pipeline for all requests:**

1. Uvicorn → FastAPI `app`
2. CORS middleware (`main.py`)
3. Router → endpoint handler
4. Pydantic validation
5. Service layer invocation
6. Structured response or `HTTPException`

RAG endpoints add steps 4b (request ID middleware, Phase 14) and service calls through `RAGService` instead of direct LLM.

## 4. Alternatives Considered

| Alternative | Notes |
|-------------|-------|
| GraphQL | Overkill for farmer mobile clients |
| gRPC internal + REST edge | Future option if splitting services |
| LangServe as HTTP layer | Couples serving to LangChain |

## 5. Why Alternative Was Not Selected

REST + FastAPI matches the existing React `api.js` client, OpenAPI/Swagger for debugging, and standard interview expectations.

## 6. Tradeoffs

| Pro | Con |
|-----|-----|
| Swagger auto-docs | REST verbosity for complex queries |
| Pydantic validation at boundary | Duplicate DTOs if not careful |

## 7. Performance Implications

- Sync handlers today; RAG `/ask` should use `async def` + `httpx`/`groq` async to avoid blocking workers
- Request ID enables per-stage timing headers (`X-Retrieval-Ms`, Phase 14)

## 8. Scaling Considerations

- Stateless handlers → scale Uvicorn workers behind load balancer
- No sticky sessions required for `/ask`
- Upload endpoint may use background task or queue for ingestion (Phase 18)

## 9. Production Considerations

- Rate limiting at API gateway (future)
- Max body size for PDF upload
- Timeouts: 30s default for `/ask`, 120s for `/documents/upload` + ingest

## 10. Failure Cases

| Stage | Client sees |
|-------|-------------|
| Validation error | 422 + Pydantic detail |
| Qdrant down | 503 on RAG routes |
| LLM rate limit | 429 with retry-after |
| Unhandled exception | 500; logged with request_id |

## 11. Edge Cases

- `ChatRequest` accepts both `message` and `question` fields for backward compatibility
- Empty question → 400 before embedding call (saves cost)

## 12. Security Concerns

- CORS restricted via `CORS_ORIGINS` env
- File upload virus scan (future); PDF-only MIME whitelist

## 13. Cost Considerations

- Reject oversized/invalid requests before LLM invocation
- `/search` endpoint retrieves without LLM — cheaper debug path

## 14. Common Interview Questions

**Q: Trace a `/api/chat` request today.**  
A: `routes.py` → `get_chatbot_response()` → OpenRouter Gemini — no retrieval.

**Q: Trace a future `/api/v1/ask` request.**  
A: See diagram below.

## 15. Deep Interview Questions

**Q: Where do you inject dependencies?**  
A: `core.dependencies`: `get_rag_service()`, `get_vector_store()` as FastAPI `Depends()` — enables test overrides.

**Q: How do you avoid blocking the event loop during local embedding?**  
A: `run_in_executor` for CPU embed or dedicated embedding microservice.

## 16. Best Possible Answers

Narrate the path naming each layer's **single job**. Stress validation happens once at the API boundary.

## 17. Diagrams

### Current: `POST /api/chat`

```
Client
  │
  ▼
FastAPI (CORS)
  │
  ▼
routes.chat_with_assistant()
  │
  ▼
ChatRequest validation (Pydantic)
  │
  ▼
services.chatbot.get_chatbot_response()
  │
  ▼
OpenRouter API (Gemini)
  │
  ▼
JSON { success, response, timestamp }
```

### Planned: `POST /api/v1/ask`

```
Client
  │
  ▼
FastAPI + RequestID middleware
  │
  ▼
endpoints/rag.ask_question()
  │
  ▼
AskRequest validation
  │
  ▼
RAGService.ask()
  ├── embeddings.embed_query()
  ├── retrieval.search()
  ├── ContextBuilder.build()
  ├── PromptTemplates.assemble()
  ├── llm.generate()
  └── CitationExtractor.attach()
  │
  ▼
AskResponse { answer, citations[], latencies{} }
```

### Planned: `POST /api/v1/documents/upload`

```
Client (multipart PDF)
  │
  ▼
endpoints/documents.upload()
  │
  ▼
Save to data/raw/ + update manifest
  │
  ▼
Background: IngestionPipeline.run()
  │
  ▼
202 Accepted { document_id, status: "processing" }
```

### Existing ML/utility routes (unchanged)

| Method | Path | Service |
|--------|------|---------|
| POST | `/api/advisory` | `ml.inference` |
| POST | `/api/weather` | `services.weather` |
| POST | `/api/market-prices` | `services.market` |
| GET | `/` | Health-ish metadata |

## 18. References

- `backend/app/main.py`
- `backend/app/api/routes.py`
- FastAPI dependency injection docs
