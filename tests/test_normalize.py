"""Tests for Gojri text normalization and script detection."""

from __future__ import annotations

import pytest

from gojrilang.normalize import (
    detect_script,
    normalize,
    normalize_for_search,
    strip_diacritics,
)


def test_script_detection() -> None:
    assert detect_script("گھوڑو") == "perso-arabic"
    assert detect_script("घोड़ो") == "devanagari"
    assert detect_script("ghoṛo") == "latin"
    assert detect_script("") == "unknown"
    assert detect_script("   ") == "unknown"


def test_normalize_whitespace() -> None:
    raw = "  گھوڑو   تیز   دوڑے    ہے  \n"
    norm = normalize(raw)
    assert norm == "گھوڑو تیز دوڑے ہے"


def test_normalize_preserve_original() -> None:
    raw = "  ghoṛo   "
    norm, orig = normalize(raw, preserve_original=True)
    assert norm == "ghoṛo"
    assert orig == raw


def test_strip_arabic_diacritics() -> None:
    # Arabic with fatha/kasra/damma/shadda
    with_tashkeel = "گھوڑاَُِّ"
    stripped = strip_diacritics(with_tashkeel, script="perso-arabic")
    assert stripped == "گھوڑا"


def test_strip_latin_diacritics() -> None:
    text = "ghoṛo pāṇi"
    stripped = strip_diacritics(text, script="latin")
    assert stripped == "ghoro pani"


def test_normalize_for_search() -> None:
    assert normalize_for_search("GHOṚO!") == "ghoro"
    assert normalize_for_search("گھوڑو،") == "گھوڑو"

