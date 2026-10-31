"""Tests for verified translation interface."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.translation import translate


def test_exact_phrase_translation_gojri_to_english() -> None:
    res = translate("تسی کس طرح چھو؟", source="gojri", target="english")
    assert res.status == "exact_match"
    assert res.confidence == 1.0
    assert "How are you" in res.text


def test_exact_phrase_translation_english_to_gojri() -> None:
    res = translate("How are you?", source="english", target="gojri")
    assert res.status == "exact_match"
    assert "تسی کس طرح چھو" in res.text


def test_translation_to_hindi() -> None:
    res = translate("تہاڈو ناں کے ہے؟", source="gojri", target="hindi")
    assert res.status == "exact_match"
    assert "आपका नाम क्या है" in res.text


def test_single_word_lexical_fallback() -> None:
    res = translate("گھوڑو", source="gojri", target="english")
    assert res.status == "lexical_match"
    assert res.text == "horse"
    assert res.confidence > 0.8


def test_unsupported_language_pair() -> None:
    res = translate("Hello", source="english", target="swahili")
    assert res.status == "unsupported_pair"
    assert res.confidence == 0.0


def test_not_found_does_not_hallucinate() -> None:
    text = "The quantum fluctuations of the cosmos"
    res = translate(text, source="english", target="gojri")
    assert res.status == "not_found"
    assert res.confidence == 0.0
    assert "No verified translation available" in res.text

