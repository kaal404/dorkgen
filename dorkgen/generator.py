"""High-level, user-facing generation API.

This is what the CLI/TUI calls. It resolves profiles/categories/keyword
packs/templates into engine inputs, delegates the actual combination work to
``DorkEngine``, and wraps the result in a ``QuerySet``.
"""
from __future__ import annotations

import datetime
import time
from typing import Optional

from .engine import DorkEngine
from .keywordpacks import KEYWORD_PACKS
from .models import QuerySet
from .profiles import CATEGORIES, PROFILES
from .templates import TEMPLATES

_engine = DorkEngine()


def generate_queries(domain: str, categories: Optional[list[str]] = None,
                      keyword_packs: Optional[list[str]] = None,
                      selected_templates: Optional[list[str]] = None,
                      min_risk: int = 0, max_results: int = 0,
                      profile: str = "", filetypes: Optional[list[str]] = None) -> QuerySet:
    """Generate a scored, deduplicated ``QuerySet`` for ``domain``.

    Kept backward-compatible with the original single-file API so existing
    callers/scripts don't need to change.
    """
    start = time.perf_counter()

    target_cats = categories if categories else list(CATEGORIES.keys())
    target_packs = keyword_packs if keyword_packs else list(KEYWORD_PACKS.keys())

    target_templates = [t for t in TEMPLATES if t.category in target_cats or t.category == "general"]
    if selected_templates:
        target_templates = [t for t in target_templates if t.name in selected_templates]

    keyword_pool = _engine.collect_keywords(target_packs)

    queries, duplicates = _engine.generate(
        domain, target_templates, keyword_pool,
        filetypes=filetypes, min_risk=min_risk, max_results=max_results,
    )

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return QuerySet(
        queries=queries, generated_at=datetime.datetime.now().isoformat(),
        domain=domain, profile=profile, total=len(queries),
        duplicates_removed=duplicates, generation_time_ms=elapsed_ms,
    )


def generate_for_profile(domain: str, profile_name: str, min_risk: int = 0,
                          max_results: int = 0) -> QuerySet:
    """Generate a query set using a named built-in profile."""
    profile = PROFILES.get(profile_name, PROFILES["bug_bounty"])
    return generate_queries(
        domain,
        categories=list(profile["cats"]),  # type: ignore[arg-type]
        keyword_packs=list(profile["packs"]),  # type: ignore[arg-type]
        min_risk=min_risk, max_results=max_results, profile=profile_name,
    )


def generate_custom(domain: str, operator: str, keyword: str, filetype: str = "",
                     exact: bool = True) -> str:
    """Render a single one-off dork from explicit user input (Query Builder)."""
    from .models import QueryTemplate

    ops = ("site", "filetype", operator) if filetype else ("site", operator)
    template = QueryTemplate(
        name="custom", description="User-built query", category="custom",
        subcategory="builder", operators=ops, filetypes=(filetype,) if filetype else (),
        risk_base=7, exact=exact,
    )
    return template.render(domain, keyword, filetype or None)


def search_templates(query: str = "", category: str = "", technology: str = "",
                      min_risk: int = 0) -> list:
    """Search/filter the template catalog — powers the CLI's search screens."""
    query_lower = query.lower()
    results = []
    for tmpl in TEMPLATES:
        if category and tmpl.category != category:
            continue
        if technology and tmpl.technology != technology:
            continue
        if tmpl.risk_base < min_risk:
            continue
        if query_lower and query_lower not in tmpl.name.lower() and query_lower not in tmpl.description.lower():
            continue
        results.append(tmpl)
    return results


def search_keywords(query: str = "", category: str = "", technology: str = "",
                     min_risk: int = 0) -> list:
    """Search/filter across all keyword packs — powers the CLI's search screens."""
    query_lower = query.lower()
    results = []
    for pack in KEYWORD_PACKS.values():
        for kw in pack["keywords"]:  # type: ignore[index]
            if category and kw.category != category:
                continue
            if technology and kw.technology != technology:
                continue
            if kw.risk < min_risk:
                continue
            if query_lower and query_lower not in kw.keyword.lower():
                continue
            results.append(kw)
    return results
