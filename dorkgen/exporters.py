"""Export generated queries to TXT/Markdown/CSV/JSON/HTML.

The original CSV export was broken — it wrote a header with no newline and
concatenated every row with no delimiter, producing an unreadable single
line rather than valid CSV (see AUDIT.md). This version uses the stdlib
``csv`` module and includes risk score, priority, category, source
template, and reason columns for every format, as requested.
"""
from __future__ import annotations

import csv
import datetime
import html as html_lib
import io
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .constants import VERSION
from .models import ScoredQuery


def _filter_and_group(queries: list[ScoredQuery], min_priority: float,
                       by_category: bool) -> tuple[list[ScoredQuery], dict[str, list[ScoredQuery]]]:
    if min_priority > 0:
        queries = [q for q in queries if q.priority >= min_priority]
    grouped: dict[str, list[ScoredQuery]] = defaultdict(list)
    if by_category:
        for q in queries:
            grouped[q.category or "uncategorized"].append(q)
    return queries, grouped


def _export_txt(queries: list[ScoredQuery], grouped: dict[str, list[ScoredQuery]], by_category: bool) -> str:
    lines = [f"# DorkGEN v{VERSION}", f"# Generated: {datetime.datetime.now().isoformat()}",
              f"# Total: {len(queries)}", ""]
    if by_category:
        for cat, qs in sorted(grouped.items()):
            lines.append(f"## {cat.upper()}")
            lines.extend(q.query for q in qs)
            lines.append("")
    else:
        lines.extend(q.query for q in queries)
    return "\n".join(lines)


def _export_md(queries: list[ScoredQuery], grouped: dict[str, list[ScoredQuery]], by_category: bool) -> str:
    lines = [f"# DorkGEN v{VERSION}", "", f"**{len(queries)} Google Dorks**", ""]
    if by_category:
        groups = sorted(grouped.items())
    else:
        groups = [("all", queries)]
    for cat, qs in groups:
        if by_category:
            lines.append(f"## {cat.upper()}")
        lines.append("| Dork | Risk | Priority | Category | Template | Reason |")
        lines.append("|---|---|---|---|---|---|")
        for q in qs:
            lines.append(
                f"| `{q.query}` | {q.risk_score} | {q.priority} | {q.category} "
                f"| {q.source_template} | {q.reason} |"
            )
        lines.append("")
    return "\n".join(lines)


def _export_csv(queries: list[ScoredQuery]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["query", "risk_score", "priority", "confidence", "complexity",
                      "category", "subcategory", "technology", "source_template", "reason"])
    for q in queries:
        writer.writerow([q.query, q.risk_score, q.priority, q.confidence, q.complexity,
                          q.category, q.subcategory, q.technology, q.source_template, q.reason])
    return buffer.getvalue()


def _export_json(queries: list[ScoredQuery]) -> str:
    return json.dumps({
        "version": VERSION,
        "generated_at": datetime.datetime.now().isoformat(),
        "total": len(queries),
        "queries": [q.to_dict() for q in queries],
    }, indent=2)


def _export_html(queries: list[ScoredQuery]) -> str:
    def esc(value: object) -> str:
        return html_lib.escape(str(value))

    rows = "".join(
        f"<tr><td>{i}</td><td><code>{esc(q.query)}</code></td>"
        f"<td>{q.risk_score}</td><td>{q.priority}</td><td>{esc(q.category)}</td>"
        f"<td>{esc(q.source_template)}</td><td>{esc(q.reason)}</td></tr>"
        for i, q in enumerate(queries, 1)
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>DorkGEN v{VERSION} Export</title>"
        "<style>body{font-family:sans-serif}table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #ccc;padding:6px 10px;text-align:left}"
        "th{background:#222;color:#fff}code{color:#0a6}</style></head><body>"
        f"<h2>DorkGEN v{VERSION} — {len(queries)} queries</h2>"
        "<table><tr><th>#</th><th>Google Dork</th><th>Risk</th><th>Priority</th>"
        f"<th>Category</th><th>Template</th><th>Reason</th></tr>{rows}</table></body></html>"
    )


_EXPORTERS = {
    "txt": lambda qs, g, by_cat: _export_txt(qs, g, by_cat),
    "md": lambda qs, g, by_cat: _export_md(qs, g, by_cat),
    "csv": lambda qs, g, by_cat: _export_csv(qs),
    "json": lambda qs, g, by_cat: _export_json(qs),
    "html": lambda qs, g, by_cat: _export_html(qs),
}


def export_queries(queries: list[ScoredQuery], format: str = "txt", filepath: Optional[str] = None,
                    min_priority: float = 0, by_category: bool = False) -> str:
    """Render ``queries`` to ``format`` and optionally write to ``filepath``."""
    filtered, grouped = _filter_and_group(queries, min_priority, by_category)
    exporter = _EXPORTERS.get(format)
    if exporter is None:
        content = "\n".join(q.query for q in filtered)
    else:
        content = exporter(filtered, grouped, by_category)

    if filepath:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return content
