"""Tests for Gojri dialect and regional variation subsystem."""

from __future__ import annotations

import pytest

from gojrilang.dialects import (
    compare_variants,
    get_dialect_profile,
    list_dialect_profiles,
)
from gojrilang.exceptions import DialectProfileNotFoundError


def test_list_dialect_profiles() -> None:
    profiles = list_dialect_profiles()
    assert len(profiles) >= 4
    ids = {p.id for p in profiles}
    assert "jk_poonchi" in ids
    assert "western_hazara" in ids
    assert "himachal" in ids
    assert "southern_rajasthani" in ids


def test_get_dialect_profile() -> None:
    p = get_dialect_profile("jk_poonchi")
    assert p.id == "jk_poonchi"
    assert "Poonch" in p.region
    assert len(p.phonological_features) > 0
    assert "pani" in p.lexical_variants or "water" in p.lexical_variants or len(p.lexical_variants) > 0


def test_get_missing_dialect_profile_raises() -> None:
    with pytest.raises(DialectProfileNotFoundError):
        get_dialect_profile("non_existent_dialect_id")


def test_compare_variants() -> None:
    diff = compare_variants("water")
    assert isinstance(diff, dict)
    comparisons = diff.get("comparisons", diff)
    assert len(comparisons) >= 2
    # Also test case-insensitivity
    variants_water = compare_variants("WATER")
    assert len(variants_water.get("comparisons", variants_water)) >= 2


def test_compare_variants_specific_profiles() -> None:
    diff = compare_variants("water", profiles=["jk_poonchi", "western_hazara"])
    comparisons = diff.get("comparisons", diff)
    assert "jk_poonchi" in comparisons
    assert "western_hazara" in comparisons
    assert "southern_rajasthani" not in comparisons
