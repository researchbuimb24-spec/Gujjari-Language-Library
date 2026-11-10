"""Tests for the Gojri multilingual dictionary subsystem."""

from __future__ import annotations

import pytest

import gojrilang
from gojrilang.dictionary import lookup


def test_exact_lookup_perso_arabic() -> None:
    entry = lookup("گھوڑو")
    assert entry is not None
    assert entry.word == "گھوڑو"
    assert entry.pos == "noun"
    assert entry.meaning_en == "horse"
    assert entry.meaning_ur == "گھوڑا"
    assert entry.verification_status == "verified"
    assert "SHARMA_1982" in entry.source


def test_exact_lookup_devanagari() -> None:
    entry = lookup("घोड़ो")
    assert entry is not None
    assert entry.word == "گھوڑو"
    assert entry.meaning_en == "horse"


def test_exact_lookup_roman() -> None:
    entry = lookup("ghoṛo")
    assert entry is not None
    assert entry.meaning_en == "horse"


def test_case_insensitive_and_diacritic_tolerance() -> None:
    # Lowercase / stripped diacritic roman search
    entry1 = lookup("GHOṚO")
    assert entry1 is not None
    assert entry1.meaning_en == "horse"

    entry2 = lookup("ghoro")
    assert entry2 is not None
    assert entry2.meaning_en == "horse"


def test_missing_word_returns_none() -> None:
    assert lookup("nonexistent_word_xyz_123") is None
    assert lookup("") is None
    assert lookup("   ") is None


def test_example_sentence_present() -> None:
    entry = lookup("پاݨی")
    assert entry is not None
    assert entry.example_sentence is not None
    assert "پاݨی" in entry.example_sentence.text
    assert entry.example_sentence.translation_en != ""


def test_entry_string_and_dict_representation() -> None:
    entry = lookup("بکرو")
    assert entry is not None
    entry_dict = entry.to_dict()
    assert isinstance(entry_dict, dict)
    assert entry_dict["word"] == "بکرو"
    assert "he-goat" in str(entry)


def test_lookup_all() -> None:
    entries = gojrilang.lookup_all("گھوڑو")
    assert len(entries) >= 1
    assert entries[0].word == "گھوڑو"


def test_get_word_details() -> None:
    entry = gojrilang.get_word_details("word_001")
    assert entry is not None
    assert entry["id"] == "word_001"
    assert entry["word"] == "گھوڑو"


def test_find_synonyms() -> None:
    # Test on a word that has synonyms or returns a list
    syns = gojrilang.find_synonyms("گھوڑو")
    assert isinstance(syns, list)


def test_get_word_variants() -> None:
    variants = gojrilang.get_word_variants("گھوڑو")
    assert isinstance(variants, dict)
    assert "alternative_spellings" in variants
    assert len(variants["alternative_spellings"]) >= 1


def test_new_lexical_items_lookup() -> None:
    chah = lookup("چاہ")
    assert chah is not None
    assert chah.meaning_en == "tea"
    assert chah.pos == "noun"
    assert chah.gender == "feminine"

    roti = lookup("रोटी")
    assert roti is not None
    assert "bread" in roti.meaning_en

    rukkh = lookup("rukkh")
    assert rukkh is not None
    assert rukkh.meaning_en == "tree"

    sohno = lookup("سوہݨو")
    assert sohno is not None
    assert "beautiful" in sohno.meaning_en
    assert sohno.pos == "adjective"



