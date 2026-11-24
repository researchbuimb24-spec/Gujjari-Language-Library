"""Tests for the unified Gojri object-oriented facade class and namespaces."""

import pytest
from gojrilang import Gojri


def test_gojri_facade_initialization():
    gju = Gojri()
    assert hasattr(gju, "dictionary")
    assert hasattr(gju, "grammar")
    assert hasattr(gju, "scripts")
    assert hasattr(gju, "dialects")
    assert hasattr(gju, "literature")
    assert hasattr(gju, "epics")
    assert hasattr(gju, "songs")
    assert hasattr(gju, "folklore")
    assert hasattr(gju, "corpus")
    assert hasattr(gju, "nlp")
    assert hasattr(gju, "audio")
    assert hasattr(gju, "verification")
    assert hasattr(gju, "vocabulary")


def test_gojri_facade_dictionary():
    gju = Gojri()
    entry = gju.dictionary.lookup("پانی")
    assert entry is not None
    assert entry.word in ("پاݨی", "پانی")

    results = gju.dictionary.search("water")
    assert len(results) >= 1

    trans = gju.dictionary.translate("گھر", target="english")
    assert trans is not None

    details = gju.dictionary.get_word_details("word_001")
    assert details is not None
    assert details["id"] == "word_001"
    assert "word" in details


def test_gojri_facade_grammar():
    gju = Gojri()
    rules = gju.grammar.list_rules()
    assert len(rules) >= 15

    analysis = gju.grammar.analyze("اساں بکریاں چاریاں۔")
    assert "tokens" in analysis


def test_gojri_facade_scripts():
    gju = Gojri()
    script = gju.scripts.detect("گھوڑو")
    assert "perso" in script.lower() or "arabic" in script.lower()
    assert gju.scripts.is_rtl("گھوڑو") is True

    norm = gju.scripts.normalize("  پانی  ")
    assert norm == "پانی"

    norm_nfd = gju.scripts.normalize("  پانی  ", form="NFD")
    assert norm_nfd is not None

    trans = gju.scripts.transliterate("گھوڑو", target="roman")
    assert "gh" in trans

    trans_dev = gju.scripts.transliterate("ghoṛo", source_script="roman", target_script="devanagari")
    assert "घो" in trans_dev


def test_gojri_facade_epics():
    gju = Gojri()
    epics = gju.epics.list_epics()
    assert len(epics) >= 2

    ch = gju.epics.get_chapter(book="ramayana", chapter=1)
    assert ch.chapter_num == 1
    assert len(ch.verses) >= 1


def test_gojri_facade_songs():
    gju = Gojri()
    songs = gju.songs.list()
    assert len(songs) >= 7

    cats = gju.songs.categories()
    assert len(cats) >= 4


def test_gojri_facade_folklore():
    gju = Gojri()
    riddles = gju.folklore.list_riddles()
    assert len(riddles) >= 1

    customs = gju.folklore.list_customs()
    assert len(customs) >= 1

    proverbs = gju.folklore.list_proverbs()
    assert len(proverbs) >= 5


def test_gojri_facade_corpus():
    gju = Gojri()
    stats = gju.corpus.statistics()
    assert stats.total_documents >= 10
    assert stats.total_tokens >= 50


def test_gojri_facade_nlp():
    gju = Gojri()
    tokens = gju.nlp.tokenize("اساں بکریاں چاریاں۔")
    assert len(tokens) >= 3

    check = gju.nlp.spell_check("پانی")
    assert check["is_correct"] is True


def test_gojri_facade_vocabulary():
    gju = Gojri()
    summary = gju.vocabulary.summary()
    assert summary["verified_headwords_count"] >= 200

    headwords = gju.vocabulary.headwords()
    assert len(headwords) >= 200
