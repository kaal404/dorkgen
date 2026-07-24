"""The low-level dork-combination engine.

``DorkEngine`` takes templates, keyword pools, and filetype lists and
produces deduplicated, scored queries. It knows nothing about profiles or
CLI concerns — that orchestration lives in ``generator.py``. Keeping the two
separate is what makes each independently testable.
"""
from __future__ import annotations

from typing import Iterable, Optional

from .keywordpacks import KEYWORD_PACKS
from .models import Keyword, QueryTemplate, ScoredQuery
from .operators import FILETYPES
from .scoring import score_query
from .validators import validate_domain

#: How many keyword entries a single template is allowed to cross against,
#: and how many filetypes — bounds the combinatorial explosion of a single
#: template while still producing meaningful variety across a whole run.
MAX_KEYWORDS_PER_TEMPLATE = 6
MAX_FILETYPES_PER_TEMPLATE = 3


class DorkEngine:
    """Stateless-per-call combination engine (safe to reuse/share)."""

    def __init__(self, keyword_packs: Optional[dict] = None,
                 filetypes: Optional[dict] = None) -> None:
        self._packs = keyword_packs if keyword_packs is not None else KEYWORD_PACKS
        self._filetypes = filetypes if filetypes is not None else FILETYPES

    def collect_keywords(self, pack_names: Iterable[str]) -> list[Keyword]:
        collected: list[Keyword] = []
        for pack_name in pack_names:
            pack = self._packs.get(pack_name)
            if pack:
                collected.extend(pack["keywords"])  # type: ignore[index]
        return collected

    def _keywords_for_template(self, template: QueryTemplate,
                                pool: list[Keyword]) -> list[Keyword]:
        if template.keywords:
            return [Keyword(k, template.category, template.risk_base) for k in template.keywords]
        matching = [k for k in pool if k.category == template.category]
        if not matching:
            matching = pool[: MAX_KEYWORDS_PER_TEMPLATE * 2] or [
                Keyword("sensitive", template.category or "general", 5)
            ]
        return matching[:MAX_KEYWORDS_PER_TEMPLATE]

    def _filetypes_for_template(self, template: QueryTemplate,
                                 allowed: Optional[list[str]]) -> list[str]:
        if template.filetypes:
            fts = list(template.filetypes)
        elif allowed:
            fts = allowed
        else:
            fts = list(self._filetypes.keys())
        return fts[:MAX_FILETYPES_PER_TEMPLATE]

    def generate(self, domain: str, templates: Iterable[QueryTemplate],
                 keyword_pool: list[Keyword], filetypes: Optional[list[str]] = None,
                 min_risk: int = 0, max_results: int = 0) -> tuple[list[ScoredQuery], int]:
        """Cross ``templates`` against ``keyword_pool``/``filetypes`` for
        ``domain``, returning ``(scored_queries, duplicate_count)``.
        """
        domain = validate_domain(domain)
        results: list[ScoredQuery] = []
        seen: set[str] = set()
        duplicates = 0

        needs_filetype = lambda t: "filetype" in t.operators or "ext" in t.operators  # noqa: E731

        for template in templates:
            kws = self._keywords_for_template(template, keyword_pool)
            fts = self._filetypes_for_template(template, filetypes) if needs_filetype(template) else [None]

            for kw_entry in kws:
                for ft in fts:
                    query = template.render(domain, kw_entry.keyword, ft)
                    if query in seen:
                        duplicates += 1
                        continue
                    seen.add(query)

                    scored = score_query(
                        query, template.category, template.subcategory,
                        template.technology or kw_entry.technology,
                        max(template.risk_base, kw_entry.risk),
                        source_template=template.name,
                    )
                    if scored.risk_score >= min_risk:
                        results.append(scored)

            if max_results and len(results) >= max_results * 2:
                # Generate a healthy surplus so sorting/truncation below still
                # yields the highest-priority results, without generating
                # unboundedly for very broad requests.
                break

        results.sort(key=lambda q: q.priority, reverse=True)
        if max_results:
            results = results[:max_results]
        return results, duplicates
