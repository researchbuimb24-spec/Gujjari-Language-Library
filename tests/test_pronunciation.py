"""Tests for Gojri phonetics, pronunciation, and audio subsystem."""

from __future__ import annotations

from gojrilang.pronunciation import (
    AudioReference,
    PhoneticInfo,
    get_audio,
    get_phonetics,
)


def test_get_phonetics_known_word() -> None:
    phon = get_phonetics("گھوڑو")
    assert phon is not None
    assert isinstance(phon, PhoneticInfo)
    assert phon.word == "گھوڑو"
    assert "/ɡ" in phon.ipa or "gho" in phon.phonetic_spelling
    assert phon.syllables >= 1
    assert phon.status == "verified"


def test_get_phonetics_entry_id() -> None:
    phon = get_phonetics("word_001")
    assert phon is not None
    assert phon.status == "verified"
    assert phon.word == "گھوڑو"


def test_get_phonetics_romanized_word() -> None:
    phon = get_phonetics("ghoṛo")
    assert phon is not None
    assert phon.status == "verified"


def test_get_phonetics_unindexed_word() -> None:
    phon = get_phonetics("کتاب")
    assert phon is not None
    assert phon.status in ("provisional", "rule_derived")
    assert phon.ipa.startswith("/")


def test_get_phonetics_empty_returns_none() -> None:
    assert get_phonetics("") is None
    assert get_phonetics("   ") is None


def test_get_audio_reference() -> None:
    audio = get_audio("گھوڑو")
    assert isinstance(audio, AudioReference)
    assert audio.word == "گھوڑو"
    assert audio.status == "not_recorded"
    assert "http" in (audio.audio_url or "")
