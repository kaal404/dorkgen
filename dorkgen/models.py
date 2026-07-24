"""Typed data models shared across the engine, exporters, and UI."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class Operator:
    """A single Google search operator, e.g. ``site:`` or ``intitle:``."""

    name: str
    description: str = ""
    #: If True, the value should generally be wrapped in quotes when it
    #: contains whitespace (intitle/intext/inurl-style operators).
    quote_multiword: bool = True

    def render(self, value: str) -> str:
        value = value.strip()
        if self.quote_multiword and (" " in value or "\t" in value):
            value = f'"{value}"'
        return f"{self.name}:{value}"


@dataclass(frozen=True)
class FileType:
    extension: str
    category: str = "general"
    risk_base: int = 3
    description: str = ""


@dataclass(frozen=True)
class Keyword:
    keyword: str
    category: str = "general"
    risk: int = 5
    tags: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    technology: str = ""


@dataclass
class QueryTemplate:
    """A reusable recipe for combining operators, keywords, and filetypes.

    ``render()`` is the single source of truth for turning a template into a
    query string — the generation engine always calls this rather than
    re-implementing string concatenation, so there is exactly one place that
    knows how a dork is assembled.
    """

    name: str
    description: str
    category: str
    subcategory: str
    operators: tuple[str, ...]
    keywords: tuple[str, ...] = field(default_factory=tuple)
    filetypes: tuple[str, ...] = field(default_factory=tuple)
    risk_base: int = 5
    technology: str = ""
    exact: bool = False
    exclude: tuple[str, ...] = field(default_factory=tuple)
    use_or: bool = False

    def render(self, domain: str, keyword: str, filetype: Optional[str] = None,
               operator_registry: Optional[dict[str, Operator]] = None) -> str:
        from .operators import OPERATORS  # local import avoids a cycle

        ops = operator_registry or OPERATORS
        parts: list[str] = [ops["site"].render(domain)]

        kw_value = f'"{keyword}"' if self.exact and " " not in keyword else keyword

        for op_name in self.operators:
            if op_name == "site":
                continue
            op = ops.get(op_name)
            if op is None:
                continue
            if op_name in ("filetype", "ext"):
                ft = filetype or (self.filetypes[0] if self.filetypes else None)
                if ft:
                    parts.append(f"{op_name}:{ft}")
            elif op_name in ("cache", "related", "info"):
                parts.append(op.render(domain))
            else:
                parts.append(op.render(kw_value))

        if self.use_or and len(self.keywords) > 1:
            or_group = " OR ".join(f'"{k}"' if " " in k else k for k in self.keywords[1:3])
            if or_group:
                parts.append(f"({kw_value} OR {or_group})")

        for term in self.exclude:
            parts.append(f"-{term}")

        return " ".join(p for p in parts if p)


@dataclass
class ScoredQuery:
    query: str
    risk_score: float = 0.0
    priority: float = 0.0
    confidence: float = 0.0
    complexity: str = "medium"
    category: str = ""
    subcategory: str = ""
    technology: str = ""
    reason: str = ""
    source_template: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QuerySet:
    queries: list[ScoredQuery] = field(default_factory=list)
    generated_at: str = ""
    domain: str = ""
    profile: str = ""
    total: int = 0
    duplicates_removed: int = 0
    generation_time_ms: float = 0.0

    def __post_init__(self) -> None:
        if self.total == 0:
            self.total = len(self.queries)


@dataclass
class Project:
    name: str
    target_domain: str = ""
    company_name: str = ""
    created_at: str = ""
    updated_at: str = ""
    profile: str = ""
    categories: list[str] = field(default_factory=list)
    keyword_packs: list[str] = field(default_factory=list)
    queries: list[ScoredQuery] = field(default_factory=list)
    export_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "target_domain": self.target_domain,
            "company_name": self.company_name, "created_at": self.created_at,
            "updated_at": self.updated_at, "profile": self.profile,
            "categories": self.categories, "keyword_packs": self.keyword_packs,
            "queries": [q.to_dict() for q in self.queries],
            "export_history": self.export_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        project = cls(
            name=data["name"],
            target_domain=data.get("target_domain", ""),
            company_name=data.get("company_name", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            profile=data.get("profile", ""),
            categories=list(data.get("categories", [])),
            keyword_packs=list(data.get("keyword_packs", [])),
            export_history=list(data.get("export_history", [])),
        )
        project.queries = [ScoredQuery(**q) for q in data.get("queries", [])]
        return project
