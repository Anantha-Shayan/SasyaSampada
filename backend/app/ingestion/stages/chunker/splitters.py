from __future__ import annotations

from collections.abc import Iterable

DEFAULT_SEPARATORS: tuple[str, ...] = (
    "\n\n",  # paragraphs
    "\n",    # lines
    ". ",    # sentences (English agri docs)
    " ",     # words
    "",      # characters (last resort)
)


def _merge_splits(
    splits: Iterable[str],
    *,
    separator: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Merge small splits into chunks respecting size and overlap (LangChain-compatible)."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    separator_len = len(separator)
    docs: list[str] = []
    current_doc: list[str] = []
    total = 0

    for piece in splits:
        piece_len = len(piece)
        overflow = (
            total + piece_len + (separator_len if current_doc else 0) > chunk_size
        )

        if overflow and current_doc:
            doc = separator.join(current_doc).strip()
            if doc:
                docs.append(doc)

            while current_doc and (
                total > chunk_overlap
                or (
                    total + piece_len + (separator_len if current_doc else 0) > chunk_size
                    and total > 0
                )
            ):
                total -= len(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                current_doc = current_doc[1:]

        current_doc.append(piece)
        total += piece_len + (separator_len if len(current_doc) > 1 else 0)

    tail = separator.join(current_doc).strip()
    if tail:
        docs.append(tail)

    return docs


def recursive_character_split(
    text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
    separators: tuple[str, ...] | None = None,
) -> list[str]:
    """
    Split text using recursive character boundaries.

    Implements the same strategy as LangChain's RecursiveCharacterTextSplitter.
    """
    if not text:
        return []

    separator_list = list(separators or DEFAULT_SEPARATORS)
    separator = separator_list[-1]
    next_separators: list[str] = []

    for index, candidate in enumerate(separator_list):
        if candidate == "":
            separator = candidate
            break
        if candidate in text:
            separator = candidate
            next_separators = separator_list[index + 1 :]
            break

    if separator:
        splits = text.split(separator)
    else:
        splits = list(text)

    good_splits: list[str] = []
    merge_buffer: list[str] = []

    for split in splits:
        if not split:
            continue
        if len(split) < chunk_size:
            merge_buffer.append(split)
        else:
            if merge_buffer:
                merged = _merge_splits(
                    merge_buffer,
                    separator=separator,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                good_splits.extend(merged)
                merge_buffer = []
            if next_separators:
                good_splits.extend(
                    recursive_character_split(
                        split,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        separators=tuple(next_separators),
                    )
                )
            else:
                good_splits.extend(
                    _merge_splits(
                        [split],
                        separator=separator,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                    )
                )

    if merge_buffer:
        good_splits.extend(
            _merge_splits(
                merge_buffer,
                separator=separator,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )

    return [chunk.strip() for chunk in good_splits if chunk.strip()]
