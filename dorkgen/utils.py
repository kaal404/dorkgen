"""Small, dependency-free helpers shared across modules."""
from __future__ import annotations

import re


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def truncate(text: str, length: int = 50, suffix: str = "...") -> str:
    if len(text) <= length:
        return text
    return text[: max(0, length - len(suffix))] + suffix


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def paginate(items: list, page: int, page_size: int) -> tuple[list, int]:
    """Return the slice for ``page`` (1-indexed) and the total page count."""
    if page_size <= 0:
        return items, 1
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    return items[start:start + page_size], total_pages
