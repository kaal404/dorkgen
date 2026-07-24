"""DorkGEN — Google Dork Intelligence Framework.

For authorized security testing, bug bounty programs, penetration testing
engagements, and defensive security research only.

Public API (kept backward-compatible with the pre-refactor single-file
version so existing scripts/imports keep working)::

    from dorkgen import generate_queries, export_queries, score_query

See ``AUDIT.md`` in the project root for the pre-refactor audit, and
``README.md`` for usage.
"""
from __future__ import annotations

from .constants import AUTHOR, VERSION
from .exporters import export_queries
from .generator import generate_custom, generate_for_profile, generate_queries
from .main import main
from .models import (FileType, Keyword, Operator, Project, QuerySet, QueryTemplate, ScoredQuery)
from .scoring import score_query

__version__ = VERSION
__author__ = AUTHOR

__all__ = [
    "__version__", "__author__",
    "generate_queries", "generate_for_profile", "generate_custom",
    "export_queries", "score_query", "main",
    "FileType", "Keyword", "Operator", "Project", "QuerySet", "QueryTemplate", "ScoredQuery",
]
