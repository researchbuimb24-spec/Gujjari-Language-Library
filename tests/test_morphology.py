"""Tests for morphological analysis and paradigm generation."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.exceptions import GojriLangError
from gojrilang.morphology import (
    analyze_word,
    generate_forms,
    list_documented_affixes,
)


def test_analyze_word_known_lexicon() -> None:
    res = analyze_word("گھوڑو")
    assert res.lemma == "گھوڑو"
    assert res.pos == "noun"
    assert res.gender == "masculine"
    assert res.verification_status == "verified"


def test_analyze_word_inflected_affix_detection() -> None:
    res = analyze_word("گھوڑیاں")
    assert res.number == "plural"
    assert any(af["affix"] == "-یاں" for af in res.affixes)


def test_list_documented_affixes() -> None:
    affixes = list_documented_affixes()
    assert len(affixes) >= 5
    assert any(a["affix"] == "-o" for a in affixes)
    assert any(a["affix"] == "-i" for a in affixes)


def test_generate_forms_masculine_noun() -> None:
    forms = generate_forms("ghoṛ", category="marked_masculine_noun")
    assert forms["direct_singular"] == "ghoṛo"
    assert forms["direct_plural"] == "ghoṛe"
    assert forms["oblique_singular"] == "ghoṛe"
    assert forms["oblique_plural"] == "ghoṛyā̃"


def test_generate_forms_perso_arabic() -> None:
    forms = generate_forms("بکر", category="marked_masculine_noun")
    assert forms["direct_singular"] == "بکرو"
    assert forms["direct_plural"] == "بکرے"
    assert forms["oblique_plural"] == "بکریاں"


def test_generate_forms_feminine_noun() -> None:
    forms = generate_forms("bakr", category="marked_feminine_noun")
    assert forms["direct_singular"] == "bakri"
    assert forms["direct_plural"] == "bakriyā̃"


def test_generate_forms_regular_verb() -> None:
    forms = generate_forms("kar", category="regular_verb")
    assert forms["infinitive"] == "karṇo"
    assert forms["habitual_masc_sg"] == "karto"
    assert forms["future_masc_sg"] == "karo go"


def test_unsupported_category_raises_error() -> None:
    with pytest.raises(GojriLangError):
        generate_forms("test", category="unsupported_mythical_category")


def test_lemmatize() -> None:
    # Direct dictionary entry
    assert gojrilang.lemmatize("گھوڑو") == "گھوڑو"
    assert gojrilang.lemmatize("ghoṛo") == "گھوڑو" or gojrilang.lemmatize("ghoṛo") == "ghoṛo"

    # Inflected plural forms
    lem = gojrilang.lemmatize("گھوڑیاں")
    assert lem in ("گھوڑو", "گھوڑ")


def test_affix_rule_traceability() -> None:
    affixes = list_documented_affixes()
    for af in affixes:
        assert "rule_id" in af
        assert af["rule_id"].startswith("RULE_")


