import pytest

from dorkgen.validators import (ValidationError, validate_domain, validate_filetype,
                                 validate_operator, validate_profile, validate_risk)


@pytest.mark.parametrize("domain", ["example.com", "sub.example.com", "*.example.com",
                                     "https://example.com/", "EXAMPLE.COM"])
def test_valid_domains(domain):
    assert validate_domain(domain)


@pytest.mark.parametrize("domain", ["", "bad domain", 'a"b.com', "-bad.com", "no_tld"])
def test_invalid_domains_raise(domain):
    with pytest.raises(ValidationError):
        validate_domain(domain)


def test_validate_filetype_known_and_unknown():
    assert validate_filetype(".ENV") == "env"
    with pytest.raises(ValidationError):
        validate_filetype("exe")


def test_validate_operator_known_and_unknown():
    assert validate_operator("SITE") == "site"
    with pytest.raises(ValidationError):
        validate_operator("nosuchop")


def test_validate_profile_known_and_unknown():
    assert validate_profile("bug_bounty") == "bug_bounty"
    with pytest.raises(ValidationError):
        validate_profile("nosuchprofile")


@pytest.mark.parametrize("value,expected", [(0, 0), ("10", 10), (5, 5)])
def test_validate_risk_in_range(value, expected):
    assert validate_risk(value) == expected


@pytest.mark.parametrize("value", [-1, 11, "20"])
def test_validate_risk_out_of_range(value):
    with pytest.raises(ValidationError):
        validate_risk(value)
