"""Tests for internal datasets and schema validation."""

from __future__ import annotations

import pytest

from gojrilang.datasets import (
    get_dataset_stats,
    load_cultural_data_raw,
    load_dictionary_entries,
    load_grammar_rules_raw,
    load_translation_data_raw,
)


def test_dictionary_entries_loaded() -> None:
    entries = load_dictionary_entries()
    assert len(entries) >= 20
    for e in entries:
        assert "id" in e
        assert "word" in e
        assert "meaning_en" in e
        assert "source" in e
        assert e["verification_status"] == "verified"


def test_grammar_rules_loaded() -> None:
    data = load_grammar_rules_raw()
    rules = data.get("rules", [])
    assert len(rules) >= 5
    for r in rules:
        assert "id" in r
        assert "category" in r
        assert "name" in r
        assert "description" in r
        assert "source" in r


def test_dataset_stats_summary() -> None:
    stats = get_dataset_stats()
    assert stats["language"] == "Gujari / Gojri (ISO 639-3: gju)"
    assert stats["dictionary"]["total_entries"] >= 20
    assert stats["dictionary"]["verified_count"] >= 20
    assert stats["grammar"]["total_rules"] >= 5
    assert stats["culture"]["total_items"] >= 5
    assert len(stats["translation"]["supported_languages"]) == 4

