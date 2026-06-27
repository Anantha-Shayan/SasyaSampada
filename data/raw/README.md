# `data/raw/`

## Purpose

Store **original, unmodified PDF files** exactly as received from upload or download.

## Rules

- Files are **write-once**. Updates create a new `version` in the manifest; the new PDF may use a new filename or replace via versioned archive policy.
- Filename must match `filename` field in `manifests/documents.json`.
- Compute `content_sha256` at first ingest and store in manifest for deduplication.
- Do not store parsed text, chunks, or embeddings here.

## Naming

`{document_id}.pdf` preferred (already used in catalog). Human-readable slugs only; no spaces.

## Production

- Move to S3/GCS with key `raw/{document_id}/v{version}/{filename}` at scale.
- Virus scan and MIME validation before write (Phase 13 upload API).
