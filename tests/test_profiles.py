import pytest

from dorkgen.keywordpacks import KEYWORD_PACKS
from dorkgen.profiles import CATEGORIES, PROFILES


def test_every_profile_pack_exists():
    """Regression test for the original ai_services/react/angular bug (AUDIT.md)."""
    for name, profile in PROFILES.items():
        for pack in profile["packs"]:
            assert pack in KEYWORD_PACKS, f"profile {name!r} references undefined pack {pack!r}"


def test_every_profile_category_exists():
    for name, profile in PROFILES.items():
        for cat in profile["cats"]:
            assert cat in CATEGORIES, f"profile {name!r} references undefined category {cat!r}"


def test_ai_services_react_angular_packs_exist():
    assert "ai_services" in KEYWORD_PACKS
    assert "react" in KEYWORD_PACKS
    assert "angular" in KEYWORD_PACKS


@pytest.mark.parametrize("name", list(PROFILES.keys()))
def test_profile_has_name_and_description(name):
    profile = PROFILES[name]
    assert profile["name"]
    assert profile["desc"]


def test_categories_have_subcategories():
    for key, cat in CATEGORIES.items():
        assert cat["subs"], f"category {key!r} has no subcategories"
