# SasyaSampada RAG — Documentation Index

Production-grade Retrieval Augmented Generation (RAG) documentation for the SasyaSampada agricultural advisory platform.

## Phase Status

| Phase | Topic | Status |
|-------|-------|--------|
| 1 | System Design & Architecture | Complete |
| 2 | Knowledge Base Organization | Complete |
| 3 | Ingestion Pipeline | Complete |
| 4 | PDF Parsing | Complete |
| 5 | Cleaning | Complete |
| 6 | Chunking | Complete |
| 7 | Metadata | Complete |
| 8 | Embeddings | Planned |

## Core Documents

| # | Document | Description |
|---|----------|-------------|
| 01 | [Project Overview](01_project_overview.md) | Goals, scope, and current state |
| 02 | [Architecture](02_architecture.md) | System design, folder structure, components |
| 03 | [Request Flow](03_request_flow.md) | HTTP request lifecycle |
| 04 | [Data Flow](04_data_flow.md) | End-to-end data movement |
| 05 | [RAG Pipeline](05_rag_pipeline.md) | Query-time RAG architecture (planned) |
| 06 | [Ingestion Pipeline](06_ingestion_pipeline.md) | Modular ingestion pipeline (Phase 3) |
| — | [Knowledge Base Organization](knowledge_base_organization.md) | Disk layout, versioning, dedup, lifecycle |
| 07 | [PDF Parsing](07_pdf_parsing.md) | PyMuPDF, pdfplumber, OCR architecture |
| 08 | [Cleaning](08_cleaning.md) | Text normalization and noise removal |
| 09 | [Chunking](09_chunking.md) | Recursive character splitting |
| 10 | [Metadata](10_metadata.md) | Rich chunk metadata and citations |
| 16 | [Scalability](16_scalability.md) | Horizontal scaling and growth path |

## Engineering Reference

| # | Document | Description |
|---|----------|-------------|
| 23 | [Engineering Decisions](23_engineering_decisions.md) | ADR-style decision log |

## Upcoming (Later Phases)

Documents 11–15, 17–22, 24–25, and `interview_master_guide.md` will be added as their corresponding implementation phases complete.
