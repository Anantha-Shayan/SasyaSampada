from __future__ import annotations

import argparse
import json
import sys

from app.core.logging import configure_logging, get_logger
from app.ingestion.factory import build_default_pipeline

logger = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="SasyaSampada document ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Run ingestion pipeline")
    ingest_parser.add_argument("--document-id", help="Catalog document_id to ingest")
    ingest_parser.add_argument(
        "--all",
        action="store_true",
        help="Ingest all active non-duplicate documents",
    )

    args = parser.parse_args(argv)
    pipeline = build_default_pipeline()

    if args.command == "ingest":
        if args.all:
            results = pipeline.run_all_active()
        elif args.document_id:
            results = [pipeline.run(args.document_id)]
        else:
            ingest_parser.error("Provide --document-id or --all")

        output = [
            {
                "success": result.success,
                "document_id": result.document_id,
                "run_id": result.run_id,
                "stages_completed": result.stages_completed,
                "error": result.error,
                "duration_ms": result.duration_ms,
                "chunks_indexed": result.indexed.chunks_indexed if result.indexed else None,
            }
            for result in results
        ]
        print(json.dumps(output, indent=2))

        if any(not result.success for result in results):
            return 1
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
