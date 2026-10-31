"""Tests for validated transliteration between Gojri scripts."""

from __future__ import annotations

import pytest

from gojrilang.exceptions import UnsupportedScriptError, UnsupportedTransliterationError
from gojrilang.transliteration import (
    supported_transliteration_pairs,
    transliterate,
)


def test_supported_pairs_list() -> None:
    pairs = supported_transliteration_pairs()
    assert ("perso-arabic", "roman") in pairs
    assert ("devanagari", "roman") in pairs
    assert ("perso-arabic", "devanagari") in pairs


def test_perso_arabic_to_roman() -> None:
    result = transliterate("گھوڑو", source="perso-arabic", target="roman")
    assert "gh" in result
    assert "ṛ" in result or "r" in result


def test_devanagari_to_roman() -> None:
    result = transliterate("पानी", source="devanagari", target="roman")
    assert "p" in result
    assert "n" in result


def test_roman_to_devanagari() -> None:
    result = transliterate("ghoṛo", source="roman", target="devanagari")
    assert "घो" in result


def test_auto_detection_transliteration() -> None:
    # Auto-detects perso-arabic source
    res1 = transliterate("پاݨی", target="roman")
    assert "p" in res1
    assert "ṇ" in res1 or "n" in res1


def test_unsupported_script_raises_error() -> None:
    with pytest.raises(UnsupportedScriptError):
        transliterate("test", source="cyrillic", target="roman")

    with pytest.raises(UnsupportedScriptError):
        transliterate("test", source="roman", target="hieroglyphs")


def test_same_script_returns_normalized() -> None:
    text = "  گھوڑو  "
    assert transliterate(text, source="perso-arabic", target="perso-arabic") == "گھوڑو"

