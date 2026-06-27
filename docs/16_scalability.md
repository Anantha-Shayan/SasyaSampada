# 16 — Scalability

## 1. Purpose

Explain how the SasyaSampada RAG architecture scales from **6 PDFs** to **millions of documents** and from **single developer laptop** to **production cluster**.

## 2. Problem Being Solved

Interviewers will ask "How does this work at scale?" even for MVPs. Architecture must not paint into corners: hardcoded paths, in-process FAISS, synchronous ingestion in request handlers.

## 3. Engineering Decision

Design for **horizontal scaling of stateless layers** and **vertical/dedicated scaling of stateful layers**:

| Layer | Scale strategy |
|-------|----------------|
| FastAPI | N replicas behind LB |
| Embedding | GPU pool / serverless burst |
| Qdrant | Sharding, replication, separate cluster |
| Ingestion | Async queue + worker pool |
| `data/raw/` | Object storage (S3) |
| LLM (Groq) | Rate limits + queue + fallback provider |

## 4. Alternatives Considered

| Alternative | Scale ceiling |
|-------------|---------------|
| Single Docker Compose forever | ~10⁴ chunks |
| Serverless only (Lambda) | Cold start on embed model |
| One giant VM | Vertical limit; SPOF |

## 5. Why Alternative Was Not Selected

Compose for dev, Kubernetes/ECS for prod is industry standard. Stateless API + managed/semi-managed Qdrant avoids reinventing distributed search.

## 6. Tradeoffs

| Early simplicity | Later work |
|------------------|------------|
| Local Qdrant in Compose | Migrate to Qdrant Cloud or K8s operator |
| Sync ingestion CLI | Add Kafka when uploads spike |
| Filesystem data dirs | S3-compatible loader interface |

## 7. Performance Implications

- HNSW index in Qdrant: sub-linear search vs. brute force
- Batch embedding amortizes model load
- API p95 dominated by LLM — scale Groq quota or add streaming (Phase 18)

## 8. Scaling Considerations

### Document count

| Scale | Architecture adjustments |
|-------|-------------------------|
| 10² docs | Current design sufficient |
| 10⁴ docs | Qdrant payload indexes on `category`, `document_id` |
| 10⁶ docs | Collection sharding by category/year; embedding service |
| 10⁷+ docs | Multi-tenant collections; dedicated search tier; BM25 hybrid |

### Query QPS

| QPS | Adjustments |
|-----|-------------|
| <10 | Single API worker |
| 10–100 | 4–8 Uvicorn workers; query embed cache |
| 100+ | Redis cache; CDN for static; read replicas |

### Ingestion throughput

- Documents updating every minute → event-driven pipeline (Kafka topic `document.updated`)
- Worker competes on `document_id` lock
- Partial updates: diff chunks by content hash

## 9. Production Considerations

- Autoscaling on CPU (API) and GPU queue depth (embed)
- Qdrant snapshot backups to object storage
- Blue/green embedding model migration: dual-write two collections → cutover

## 10. Failure Cases

| At scale | Mitigation |
|----------|------------|
| Hot shard | Reshard Qdrant collection |
| Groq 429 storm | Exponential backoff + queue |
| Disk full on worker | Lifecycle policy on `data/logs/` |

## 11. Edge Cases

- Thundering herd on new popular document — cache top queries
- Cross-region farmers — deploy API + Qdrant replica in region

## 12. Security Concerns

- Multi-tenant isolation via collection per org (future B2B)
- Rate limit per API key / farmer session

## 13. Cost Considerations

- Self-hosted Qdrant cheaper than Pinecone at 10⁶+ vectors
- Groq vs GPT-4: 10–100× cost difference at scale
- Spot GPU instances for batch re-embedding

## 14. Common Interview Questions

**Q: How would this scale to millions of documents?**  
A: Object storage for PDFs, async ingestion workers, sharded Qdrant, embedding microservice, cached query vectors, hybrid retrieval for recall.

**Q: Bottleneck at 1000 QPS?**  
A: LLM generation — batching not possible per user; need streaming, caching frequent answers, or smaller models.

## 15. Deep Interview Questions

**Q: How do you reindex without downtime?**  
A: Build `collection_v2` in background → dual-read → switch alias → delete `collection_v1`.

**Q: CAP tradeoff for Qdrant?**  
A: AP-oriented for search; tunable consistency via replication factor; accept stale reads for advisory use case.

## 16. Best Possible Answers

Show **which components are stateless** (easy scale) vs **stateful** (need planning). Reference concrete numbers from your corpus and latency budget.

## 17. Diagrams

### Scale-out topology (target production)

```
                    ┌─────────────┐
                    │     LB      │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      ┌─────────┐    ┌─────────┐    ┌─────────┐
      │ API pod │    │ API pod │    │ API pod │
      └────┬────┘    └────┬────┘    └────┬────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Qdrant  │ │ Embed    │ │  Groq    │
        │ cluster  │ │ service  │ │   API    │
        └──────────┘ └──────────┘ └──────────┘

        ┌──────────┐         ┌──────────┐
        │  Kafka   │────────▶│ Ingest   │
        │  queue   │         │ workers  │
        └──────────┘         └────┬─────┘
                                  ▼
                            ┌──────────┐
                            │ S3 raw/  │
                            └──────────┘
```

### Why this architecture is scalable

1. **Separation of read/write paths** — ingest spikes do not starve queries
2. **Interface boundaries** — swap FAISS→Qdrant→Pinecone without changing chunker
3. **Disk artifacts** — re-embed at scale without re-parsing terabytes of PDF
4. **Metadata filters** — search space shrinks per query (category, language)
5. **Stateless API** — linear horizontal scaling
6. **Progressive retrieval** — pay latency cost only when quality demands it

## 18. References

- Qdrant scaling documentation
- `docs/02_architecture.md`
- `docs/21_future_improvements.md` (planned Phase 18)
