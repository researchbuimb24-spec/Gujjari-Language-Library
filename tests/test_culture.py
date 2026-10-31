"""Tests for cultural knowledge, proverbs, and oral heritage preservation."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.culture import (
    get_cultural_item,
    list_cultural_categories,
    list_proverbs,
    search_culture,
)


def test_list_proverbs() -> None:
    proverbs = list_proverbs()
    assert len(proverbs) >= 3
    for p in proverbs:
        assert p.category == "proverbs"
        assert p.text != ""
        assert p.translation_en != ""
        assert p.verification_status == "verified"


def test_search_culture_by_english() -> None:
    results = search_culture("vessel")
    assert len(results) >= 1
    assert any("خالی برتن" in r.text for r in results)


def test_search_culture_pastoral_term() -> None:
    results = search_culture("ḍhok", category="pastoral_terms")
    assert len(results) >= 1
    assert any("ڈھوک" in r.text for r in results)


def test_get_cultural_item() -> None:
    item = get_cultural_item("CULT_PROV_01")
    assert item is not None
    assert "جیسی کرنی" in item.text
    assert "RAHI" in item.source


def test_categories_list() -> None:
    cats = list_cultural_categories()
    assert "proverbs" in cats
    assert "pastoral_terms" in cats

