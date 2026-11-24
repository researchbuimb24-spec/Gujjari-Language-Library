"""Tests for NLP processing and corpus exploration subsystem."""

import pytest
from gojrilang.corpus import (
    Corpus,
    CorpusStatistics,
    concordance,
    get_corpus,
    get_corpus_statistics,
)
from gojrilang.nlp import (
    detect_language,
    get_ngrams,
    pos_tag,
    sent_tokenize,
    spell_check,
    stem,
    text_similarity,
    tokenize,
)


def test_tokenize_perso_arabic():
    text = "اساں بکریاں چاریاں، تے باہک تے گیاں۔"
    tokens = tokenize(text)
    assert len(tokens) >= 5
    assert "اساں" in tokens
    assert "بکریاں" in tokens


def test_tokenize_without_punctuation():
    text = "پانی، روٹی، گھر!"
    tokens = tokenize(text, preserve_punctuation=False)
    assert "،" not in tokens
    assert "!" not in tokens
    assert "پانی" in tokens


def test_tokenize_devanagari():
    text = "असाँ बकरियाँ चारियाँ, ते बाहक ते गियाँ।"
    tokens = tokenize(text)
    assert "असाँ" in tokens
    assert "बकरियाँ" in tokens


def test_sent_tokenize():
    text = "اوہ گھر گیو۔ اساں بکریاں چاریاں! کی توں راضی چھیں؟"
    sents = sent_tokenize(text)
    assert len(sents) == 3


def test_pos_tag():
    text = "اساں بکریاں چاریاں"
    tagged = pos_tag(text)
    assert len(tagged) == 3
    # Check that tokens are tagged with valid POS strings
    tags = [p for t, p in tagged]
    assert all(isinstance(t, str) and len(t) > 0 for t in tags)
    assert tagged[0][1] == "PRON"  # اساں is a known pronoun


def test_spell_check_exact():
    # 'pāṇī' or 'پانی' is a verified word
    res = spell_check("پانی")
    assert res["is_correct"] is True
    assert res["suggestions"] == []


def test_spell_check_misspelling():
    # Misspelled variant
    res = spell_check("پانیک")
    assert res["is_correct"] is False
    assert len(res["suggestions"]) >= 1
    assert any(s in ("پانی", "پاݨی") for s in res["suggestions"])


def test_text_similarity():
    s1 = "اساں بکریاں چاریاں"
    s2 = "اساں بکریاں چاریاں"
    s3 = "گھر ما روٹی کھاہدی"
    assert text_similarity(s1, s2, method="jaccard") == 1.0
    sim = text_similarity(s1, s3, method="jaccard")
    assert 0.0 <= sim < 0.5


def test_detect_language():
    # Contains distinctive Gojri phonological or lexical markers (e.g. ݨ, چھوں)
    gojri_sample = "اساں دھار تے چھوں، مھاری باہک ہری ہوئی"
    res = detect_language(gojri_sample)
    assert res["language"] == "gojri"
    assert res["iso_code"] == "gju"
    assert res["confidence"] >= 0.8


def test_stem():
    assert stem("گھوڑیاں") in ("گھوڑی", "گھوڑا", "گھوڑ") or len(stem("گھوڑیاں")) < len("گھوڑیاں")


def test_ngrams():
    tokens = ["اساں", "بکریاں", "چاریاں"]
    bigrams = get_ngrams(tokens, 2)
    assert len(bigrams) == 2
    assert bigrams[0] == ("اساں", "بکریاں")


def test_corpus_statistics():
    stats = get_corpus_statistics()
    assert isinstance(stats, CorpusStatistics)
    assert stats.total_documents >= 10
    assert stats.total_sentences >= 15
    assert stats.total_tokens >= 50
    assert stats.total_unique_types >= 30
    assert stats.type_token_ratio > 0.0
    assert len(stats.top_words) >= 5


def test_corpus_concordance():
    # 'باہک' (bahak - alpine pasture) or 'رام' or 'گوجر' occurs in literature and songs
    results = concordance("باہک", window=3)
    assert isinstance(results, list)
    if len(results) > 0:
        r = results[0]
        assert "keyword" in r
        assert "left" in r
        assert "right" in r
        assert "doc_id" in r


def test_gojrilang_corpus_facade():
    import gojrilang
    assert hasattr(gojrilang, "get_corpus")
    assert hasattr(gojrilang, "concordance")
    corpus = gojrilang.get_corpus()
    assert corpus is not None
    assert len(corpus.documents) > 0
    results = gojrilang.concordance("باہک", window=2)
    assert isinstance(results, list)

