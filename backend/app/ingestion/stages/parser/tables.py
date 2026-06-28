from __future__ import annotations

from app.domain.schemas.ingestion import ParsedTable


def table_rows_to_markdown(rows: list[list[str | None]]) -> str:
    if not rows:
        return ""

    normalized: list[list[str]] = []
    for row in rows:
        normalized.append([(cell or "").strip().replace("\n", " ") for cell in row])

    if not normalized or not normalized[0]:
        return ""

    header = normalized[0]
    col_count = len(header)
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in normalized[1:]:
        padded = row + [""] * max(0, col_count - len(row))
        lines.append("| " + " | ".join(padded[:col_count]) + " |")
    return "\n".join(lines)


def parse_tables_from_rows(
    tables: list[list[list[str | None]]],
    *,
    start_index: int = 0,
) -> list[ParsedTable]:
    parsed: list[ParsedTable] = []
    for offset, rows in enumerate(tables):
        if not rows:
            continue
        markdown = table_rows_to_markdown(rows)
        if not markdown.strip():
            continue
        col_count = max(len(row) for row in rows)
        parsed.append(
            ParsedTable(
                table_index=start_index + offset,
                rows=[[(cell or "").strip() for cell in row] for row in rows],
                markdown=markdown,
                row_count=len(rows),
                col_count=col_count,
            )
        )
    return parsed
