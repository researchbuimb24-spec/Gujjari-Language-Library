"""Tests for cultural knowledge, proverbs, and oral heritage preservation."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.culture import (
    get_cultural_item,
    list_cultural_categories,
    list_items,
    list_proverbs,
    list_songs,
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


def test_list_songs() -> None:
    songs = list_songs()
    assert len(songs) >= 7
    for s in songs:
        assert s.category == "songs"
        assert s.verification_status == "verified"
    titles = [s.title for s in songs]
    assert any("Chhaint" in t for t in titles)
    assert any("Mahya" in t for t in titles)
    assert any("Singran" in t for t in titles)
    assert any("Lori" in t for t in titles)
    assert any("Dholak" in t for t in titles)


def test_list_items_category_filter() -> None:
    all_items = list_items()
    assert len(all_items) >= 30
    songs_only = list_items("songs")
    assert len(songs_only) >= 7
    assert all(i.category == "songs" for i in songs_only)


def test_search_songs() -> None:
    res = search_culture("alghoza", category="songs")
    assert len(res) >= 1
    assert "CULT_SONG_01" in [r.id for r in res]

    res_lori = search_culture("lullaby", category="songs")
    assert len(res_lori) >= 1
    assert any("lori" in r.title.lower() or "cradle" in r.explanation.lower() for r in res_lori)


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
    assert "folklore" in cats


def test_folklore_traditions() -> None:
    items = search_culture("Chhaint", category="folklore")
    assert len(items) >= 1
    assert any("چھینٹ" in i.text for i in items)
    assert items[0].verification_status == "verified"


def test_search_culture_pastoral_bahak() -> None:
    items = search_culture("bahak", category="pastoral_terms")
    assert len(items) >= 1
    assert any("بہک" in i.text for i in items)


def test_proverb_expansion_sour_grapes() -> None:
    item = get_cultural_item("CULT_PROV_05")
    assert item is not None
    assert "ہتھ نہ پجّے" in item.text
    assert "sour" in item.translation_en.lower()


