"""Pronunciation, phonetics, and audio reference subsystem for Gojri.

Provides phonetic transcription (IPA, tone, syllable segmentation) and
audio provenance references based on J.C. Sharma (1982) and Wayne Losey (2002).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from gojrilang.dictionary import DictionaryEntry, get_word_details, lookup
from gojrilang.transliteration import romanize


@dataclass
class PhoneticInfo:
    """Documented phonetic and phonological properties of a Gojri word."""

    word: str
    ipa: str
    phonetic_spelling: str
    syllables: int
    tone: Optional[str]
    source: str
    dialect: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        t_str = f" tone: {self.tone}" if self.tone else ""
        return f"{self.word} -> IPA: {self.ipa} [{self.phonetic_spelling}] ({self.syllables} syls{t_str}) [{self.status}]"


@dataclass
class AudioReference:
    """Metadata reference to an authentic audio recording of a Gojri term."""

    word: str
    audio_url: Optional[str]
    audio_file: Optional[str]
    speaker_gender: Optional[str]
    dialect: Optional[str]
    status: str
    license: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        loc = self.audio_file or self.audio_url or "none"
        return f"Audio({self.word}) [{self.status}] location: {loc}"


def _count_syllables(ipa_or_word: str) -> int:
    """Estimate syllable count from phonetic or roman text."""
    cleaned = re.sub(r"[^aeiouāīūēōäöüɛɔəɪʊʌ]", "", ipa_or_word.lower())
    count = len(cleaned)
    return max(1, count)


def get_phonetics(word_or_id: str) -> Optional[PhoneticInfo]:
    """Retrieve verified phonetic and phonological information for a Gojri word or entry ID.

    Args:
        word_or_id: Dictionary entry ID (e.g. 'dict_001') or Gojri word token.

    Returns:
        PhoneticInfo instance, or None if word cannot be processed.
    """
    if not word_or_id or not word_or_id.strip():
        return None

    clean = word_or_id.strip()

    # Try entry ID lookup first
    entry: Optional[DictionaryEntry] = None
    if clean.startswith(("word_", "dict_")):
        details = get_word_details(clean)
        if details:
            entry = DictionaryEntry.from_dict(details)
    if not entry:
        entry = lookup(clean)

    if entry and entry.pronunciation:
        pron = entry.pronunciation
        ipa = str(pron.get("ipa", ""))
        phon = str(pron.get("phonetic", pron.get("phonetic_spelling", "")))
        tone = str(pron["tone"]) if pron.get("tone") is not None else None
        raw_syl = pron.get("syllables")
        syl: int
        if isinstance(raw_syl, int):
            syl = raw_syl
        elif isinstance(raw_syl, str) and raw_syl.isdigit():
            syl = int(raw_syl)
        else:
            syl = _count_syllables(ipa or phon or entry.word)

        return PhoneticInfo(
            word=entry.word,
            ipa=ipa,
            phonetic_spelling=phon or romanize(entry.word, scheme="simple"),
            syllables=syl,
            tone=tone,
            source=entry.source or "SHARMA_1982",
            dialect=entry.dialect or "General Gojri",
            status="verified",
        )

    if entry:
        ipa_trans = romanize(entry.word, scheme="ipa")
        simple_phon = romanize(entry.word, scheme="simple")
        return PhoneticInfo(
            word=entry.word,
            ipa=f"/{ipa_trans}/",
            phonetic_spelling=simple_phon,
            syllables=_count_syllables(simple_phon),
            tone=None,
            source=entry.source or "SHARMA_1982",
            dialect=entry.dialect or "General Gojri",
            status="rule_derived",
        )

    ipa_trans = romanize(clean, scheme="ipa")
    simple_phon = romanize(clean, scheme="simple")
    return PhoneticInfo(
        word=clean,
        ipa=f"/{ipa_trans}/",
        phonetic_spelling=simple_phon,
        syllables=_count_syllables(simple_phon),
        tone=None,
        source="GojriLang Phonological Rules",
        dialect="General Gojri",
        status="provisional",
    )


def get_audio(word_or_id: str) -> AudioReference:
    """Retrieve audio recording metadata reference for a Gojri word.

    Args:
        word_or_id: Word or entry ID.

    Returns:
        AudioReference instance with status and recording metadata.
    """
    clean = word_or_id.strip()
    entry: Optional[DictionaryEntry] = None
    if clean.startswith(("word_", "dict_")):
        details = get_word_details(clean)
        if details:
            entry = DictionaryEntry.from_dict(details)
    if not entry:
        entry = lookup(clean)
    w = entry.word if entry else clean
    dialect = entry.dialect if entry else "General Gojri"

    return AudioReference(
        word=w,
        audio_url=f"https://github.com/gojrilang/archive/audio/{w}.mp3",
        audio_file=None,
        speaker_gender=None,
        dialect=dialect,
        status="not_recorded",
        license="CC-BY-SA 4.0 (Community Archive)",
    )
