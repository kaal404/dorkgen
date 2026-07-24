from dorkgen.scoring import score_query


def test_higher_keyword_risk_increases_score():
    low = score_query("site:example.com intext:foo", keyword_risk=2)
    high = score_query("site:example.com intext:foo", keyword_risk=9)
    assert high.risk_score > low.risk_score


def test_sensitive_filetype_increases_score():
    plain = score_query("site:example.com filetype:txt intext:foo", keyword_risk=5)
    sensitive = score_query("site:example.com filetype:env intext:foo", keyword_risk=5)
    assert sensitive.risk_score > plain.risk_score


def test_scores_are_bounded_0_to_10():
    q = score_query('site:example.com filetype:env intitle:"a b" intext:"secret" -test OR foo', keyword_risk=10)
    assert 0 <= q.risk_score <= 10
    assert 0 <= q.priority <= 10
    assert 0 <= q.confidence <= 10


def test_technology_is_reflected_in_reason():
    q = score_query("site:example.com intext:foo", technology="aws", keyword_risk=5)
    assert "aws" in q.reason
    assert q.technology == "aws"


def test_complexity_label_scales_with_markers():
    simple = score_query("site:example.com intext:foo", keyword_risk=5)
    complex_q = score_query('site:example.com intext:"foo" OR "bar" -baz (test*)', keyword_risk=5)
    assert simple.complexity in ("low", "medium", "high")
    assert complex_q.complexity == "high"
