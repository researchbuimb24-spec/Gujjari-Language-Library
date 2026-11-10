"""Tests for dictionary search functionality."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.dictionary import search


def test_search_by_english() -> None:
    results = search("horse", language="english")
    assert len(results) >= 1
    words = [r.word for r in results]
    assert "گھوڑو" in words


def test_search_by_hindi() -> None:
    results = search("पानी", language="hindi")
    assert len(results) >= 1
    assert any(r.word == "پاݨی" for r in results)


def test_search_by_urdu() -> None:
    results = search("بکرا", language="urdu")
    assert len(results) >= 1
    assert any(r.word == "بکرو" for r in results)


def test_search_pos_filter() -> None:
    results = search("go", pos="verb")
    assert any(r.word == "جاوݨو" for r in results)
    verbs = search("water", pos="verb")
    assert len(verbs) == 0


def test_search_limit() -> None:
    results = search("a", limit=2)
    assert len(results) <= 2


def test_empty_search_returns_empty_list() -> None:
    assert search("") == []
    assert search("   ") == []
    assert search("xyz_non_existent_term_404") == []


def test_search_expanded_vocabulary() -> None:
    winter_res = search("winter", language="english")
    assert len(winter_res) >= 1
    assert any(r.word == "سیالو" for r in winter_res)

    flute_res = search("बाँसुरी", language="hindi")
    assert len(flute_res) >= 1
    assert any(r.word == "بانسلی" for r in flute_res)

    bear_res = search("ریچھ", language="urdu")
    assert len(bear_res) >= 1
    assert any(r.word == "ریچھ" for r in bear_res)

