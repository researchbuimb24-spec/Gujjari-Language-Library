"""Tests for grammar rules engine and sentence diagnostics."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.exceptions import RuleNotFoundError
from gojrilang.grammar import get_grammar_engine, grammar_rules


def test_list_grammar_rules() -> None:
    engine = get_grammar_engine()
    all_rules = engine.list_rules()
    assert len(all_rules) >= 5

    categories = engine.list_categories()
    assert "phonology" in categories
    assert "case_and_postpositions" in categories
    assert "sentence_structure" in categories


def test_grammar_rules_helper_filtering() -> None:
    postpos_rules = grammar_rules(category="case_and_postpositions")
    assert len(postpos_rules) >= 2
    assert all(r.category == "case_and_postpositions" for r in postpos_rules)


def test_get_rule_by_id() -> None:
    engine = get_grammar_engine()
    rule = engine.get_rule("RULE_POSTPOS_01")
    assert rule.id == "RULE_POSTPOS_01"
    assert "Split-Ergative" in rule.name
    assert rule.verification_status == "verified"
    assert "SHARMA_1982" in rule.source
    assert len(rule.examples) >= 1


def test_missing_rule_raises_error() -> None:
    engine = get_grammar_engine()
    with pytest.raises(RuleNotFoundError):
        engine.get_rule("RULE_NON_EXISTENT_999")


def test_analyze_sentence_diagnostics() -> None:
    engine = get_grammar_engine()
    sentence = "چھورے نے روٹی کھادی ہے"
    analysis = engine.analyze_sentence(sentence)

    assert analysis["sentence"] == sentence
    assert analysis["status"] == "experimental_analysis"
    assert analysis["script"] == "perso-arabic"

    # Must detect ergative marker 'ne'
    markers = [m["normalized"] for m in analysis["postpositions"]]
    assert "ne" in markers

    # Must include diagnostic about ergative alignment
    obs_types = [d["type"] for d in analysis["diagnostics"]]
    assert "alignment" in obs_types
    assert "word_order" in obs_types


def test_explain_rule() -> None:
    text = gojrilang.explain_rule("RULE_POSTPOS_01")
    assert "RULE_POSTPOS_01" in text
    assert "Split-Ergative" in text
    assert "Description:" in text
    assert "Documented Examples:" in text


