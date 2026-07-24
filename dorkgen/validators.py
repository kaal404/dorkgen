"""Validation for user-supplied input.

None of this existed in the original codebase (see AUDIT.md) — domains,
filetypes, and operator names were interpolated into query strings
unchecked.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .operators import FILETYPES, OPERATORS
from .profiles import CATEGORIES, PROFILES

#: RFC-1035-ish hostname check: labels of letters/digits/hyphens, dots
#: between them, optional leading ``*.`` for wildcard domains.
_DOMAIN_RE = re.compile(
    r"^(\*\.)?(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$"
)


class ValidationError(ValueError):
    """Raised when a user-supplied value fails validation."""


def validate_domain(domain: str) -> str:
    """Validate and normalize a domain (or ``*.example.com`` wildcard).

    Raises ``ValidationError`` on anything that isn't a plausible hostname —
    in particular this rejects whitespace, quotes, and other characters that
    would otherwise corrupt a rendered dork.
    """
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain).rstrip("/")
    if not domain or not _DOMAIN_RE.match(domain):
        raise ValidationError(f"{domain!r} is not a valid domain")
    return domain


def validate_url(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"{url!r} is not a valid URL")
    return url


def validate_filetype(filetype: str) -> str:
    filetype = filetype.strip().lower().lstrip(".")
    if filetype not in FILETYPES:
        raise ValidationError(
            f"{filetype!r} is not a known filetype "
            f"(known: {', '.join(sorted(FILETYPES))})"
        )
    return filetype


def validate_operator(name: str) -> str:
    name = name.strip().lower()
    if name not in OPERATORS:
        raise ValidationError(
            f"{name!r} is not a known operator "
            f"(known: {', '.join(sorted(OPERATORS))})"
        )
    return name


def validate_profile(name: str) -> str:
    name = name.strip().lower()
    if name not in PROFILES:
        raise ValidationError(
            f"{name!r} is not a known profile "
            f"(known: {', '.join(sorted(PROFILES))})"
        )
    return name


def validate_category(name: str) -> str:
    name = name.strip().lower()
    if name not in CATEGORIES:
        raise ValidationError(
            f"{name!r} is not a known category "
            f"(known: {', '.join(sorted(CATEGORIES))})"
        )
    return name


def validate_wildcard_pattern(pattern: str) -> str:
    """Loosely validate a wildcard search pattern (``*`` allowed, no other
    Google-special characters that could break the resulting query)."""
    pattern = pattern.strip()
    if not pattern:
        raise ValidationError("pattern must not be empty")
    if '"' in pattern:
        raise ValidationError("pattern must not contain quote characters")
    return pattern


def validate_risk(value: int | str) -> int:
    ivalue = int(value)
    if not 0 <= ivalue <= 10:
        raise ValidationError("risk must be between 0 and 10")
    return ivalue
