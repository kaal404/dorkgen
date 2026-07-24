import pytest

from dorkgen.generator import generate_custom, generate_for_profile, generate_queries
from dorkgen.profiles import PROFILES
from dorkgen.validators import ValidationError


def test_generate_queries_returns_results():
    qs = generate_queries("example.com", categories=["secrets"], keyword_packs=["secrets"],
                           min_risk=0, max_results=10)
    assert qs.total > 0
    assert qs.total <= 10
    assert all("site:example.com" in q.query for q in qs.queries)


def test_generate_queries_no_duplicates():
    qs = generate_queries("example.com", categories=["secrets"], keyword_packs=["secrets"], max_results=50)
    queries = [q.query for q in qs.queries]
    assert len(queries) == len(set(queries))


def test_generate_queries_respects_min_risk():
    qs = generate_queries("example.com", min_risk=8, max_results=50)
    assert all(q.risk_score >= 8 for q in qs.queries)


def test_generate_queries_invalid_domain_raises():
    with pytest.raises(ValidationError):
        generate_queries("not a domain")


def test_generate_for_profile_every_builtin_profile_runs():
    for name in PROFILES:
        qs = generate_for_profile("example.com", name, min_risk=0, max_results=5)
        assert qs.profile == name


def test_generate_custom_renders_expected_shape():
    query = generate_custom("example.com", "inurl", "admin", filetype="", exact=True)
    assert query.startswith("site:example.com")
    assert "inurl:" in query
    assert "admin" in query


def test_ext_operator_is_distinct_from_filetype():
    from dorkgen.models import QueryTemplate

    ft_tmpl = QueryTemplate("t1", "d", "general", "general", ("site", "filetype"), filetypes=("pdf",))
    ext_tmpl = QueryTemplate("t2", "d", "general", "general", ("site", "ext"), filetypes=("pdf",))
    assert "filetype:pdf" in ft_tmpl.render("example.com", "x")
    assert "ext:pdf" in ext_tmpl.render("example.com", "x")
    assert "filetype:pdf" not in ext_tmpl.render("example.com", "x")
