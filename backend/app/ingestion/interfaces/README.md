# `app/ingestion/interfaces`

Protocol definitions for each pipeline stage. See `base.py`.

| Protocol | Implementation (Phase 3) | Enhanced in |
|----------|--------------------------|-------------|
| `DocumentLoader` | `FileSystemLoader` | — |
| `DocumentValidator` | `PdfValidator` | — |
| `DocumentParser` | `CompositePdfParser` | Phase 4 ✓ |
| `DocumentCleaner` | `AgriculturalTextCleaner` | Phase 5 ✓ |
| `DocumentChunker` | `RecursiveCharacterChunker` | Phase 6 ✓ |
| `MetadataGenerator` | `RichMetadataGenerator` | Phase 7 ✓ |
| `EmbeddingGenerator` | `HuggingFaceEmbeddingGenerator` | Phase 8 ✓ |
| `VectorStoreWriter` | `NoOpVectorStoreWriter` | Phase 9 |

Swapping a stage = inject a different implementation via `IngestionPipeline(...)` or `build_default_pipeline()`.
