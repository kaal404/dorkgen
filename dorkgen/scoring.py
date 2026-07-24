"""Risk/priority/confidence scoring for generated dorks."""
from __future__ import annotations

from .models import ScoredQuery
from .operators import FILETYPES

#: Operator prefixes counted toward "operator depth" complexity.
_DEPTH_OPERATORS = ("site:", "filetype:", "ext:", "intitle:", "inurl:", "intext:", "cache:", "related:")

#: Substrings that indicate an advanced/boolean query (each adds complexity).
_COMPLEXITY_MARKERS = ('"', " OR ", " AND ", " -", "(", "*")


def _filetype_sensitivity(query: str) -> int:
    score = 3
    for ext, ft in FILETYPES.items():
        if f"filetype:{ext}" in query or f"ext:{ext}" in query:
            score = max(score, ft.risk_base)
    return score


def _operator_depth(query: str) -> float:
    count = sum(1 for op in _DEPTH_OPERATORS if op in query)
    return min(10.0, count * 2.5)


def _complexity(query: str) -> tuple[float, str]:
    hits = sum(1 for marker in _COMPLEXITY_MARKERS if marker in query)
    score = min(10.0, hits * 2)
    label = "low" if score < 3 else ("high" if score >= 6 else "medium")
    return score, label


def score_query(query: str, category: str = "", subcategory: str = "",
                 technology: str = "", keyword_risk: int = 5,
                 source_template: str = "") -> ScoredQuery:
    """Score a rendered dork query on sensitivity, depth, and complexity."""
    kw_sensitivity = min(10, max(0, keyword_risk))
    ft_score = _filetype_sensitivity(query)
    op_count = sum(1 for op in _DEPTH_OPERATORS if op in query)
    op_depth = _operator_depth(query)
    complexity_score, complexity_label = _complexity(query)

    risk = round(min(10.0, kw_sensitivity * 0.35 + ft_score * 0.25
                      + op_depth * 0.20 + complexity_score * 0.20), 2)
    confidence = round(min(10.0, op_depth * 0.30
                            + (10 if technology else 5) * 0.40
                            + complexity_score * 0.30), 2)
    priority = round(min(10.0, risk * 0.60 + confidence * 0.40), 2)

    reasons = []
    if kw_sensitivity >= 7:
        reasons.append(f"sensitive keyword ({kw_sensitivity})")
    if ft_score >= 7:
        reasons.append(f"sensitive filetype ({ft_score})")
    if op_count >= 3:
        reasons.append(f"deep operators ({op_count})")
    if technology:
        reasons.append(f"tech: {technology}")

    return ScoredQuery(
        query=query, risk_score=risk, priority=priority, confidence=confidence,
        complexity=complexity_label, category=category, subcategory=subcategory,
        technology=technology, source_template=source_template,
        reason=" | ".join(reasons) if reasons else "standard query",
    )
