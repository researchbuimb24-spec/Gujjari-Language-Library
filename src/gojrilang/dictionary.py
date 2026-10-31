"""Multilingual dictionary module for Gojri language.

Supports exact, prefix, and fuzzy lookup, phonetic information, regional variants,
synonyms, antonyms, grammatical metadata, and provenance citations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from gojrilang.datasets import load_dictionary_entries
from gojrilang.normalize import (
    detect_script,
    normalize,
    normalize_for_search,
    strip_diacritics,
)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


@dataclass
class ExampleSentence:
    """An attested example sentence demonstrating word usage."""

    text: str
    translation_en: str
    translation_hi: str
    translation_ur: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> Optional[ExampleSentence]:
        if not data:
            return None
        return cls(
            text=data.get("text", ""),
            translation_en=data.get("translation_en", ""),
            translation_hi=data.get("translation_hi", ""),
            translation_ur=data.get("translation_ur", ""),
            text_devanagari=data.get("text_devanagari"),
            text_roman=data.get("text_roman"),
        )


@dataclass
class DictionaryEntry:
    """A verified lexical entry in the Gojri multilingual dictionary."""

    id: str
    word: str
    pos: str
    meaning_en: str
    meaning_hi: str
    meaning_ur: str
    dialect: str
    script: str
    source: str
    verification_status: str
    gender: Optional[str] = None
    word_devanagari: Optional[str] = None
    word_roman: Optional[str] = None
    example_sentence: Optional[ExampleSentence] = None
    notes: Optional[str] = None
    alternative_spellings: List[str] = field(default_factory=list)
    definitions: List[str] = field(default_factory=list)
    contextual_usage: Optional[str] = None
    pronunciation: Dict[str, Any] = field(default_factory=dict)
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)
    grammatical_info: Dict[str, Any] = field(default_factory=dict)
    license: str = "CC-BY-4.0"
    contributor: Optional[str] = None
    match_type: str = "exact"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DictionaryEntry:
        return cls(
            id=data["id"],
            word=data["word"],
            pos=data["pos"],
            meaning_en=data["meaning_en"],
            meaning_hi=data["meaning_hi"],
            meaning_ur=data["meaning_ur"],
            dialect=data.get("dialect", "general"),
            script=data.get("script", "perso-arabic"),
            source=data.get("source", "Unspecified"),
            verification_status=data.get("verification_status", "provisional"),
            gender=data.get("gender"),
            word_devanagari=data.get("word_devanagari"),
            word_roman=data.get("word_roman"),
            example_sentence=ExampleSentence.from_dict(data.get("example_sentence")),
            notes=data.get("notes"),
            alternative_spellings=data.get("alternative_spellings", []),
            definitions=data.get("definitions", []),
            contextual_usage=data.get("contextual_usage"),
            pronunciation=data.get("pronunciation", {}),
            synonyms=data.get("synonyms", []),
            antonyms=data.get("antonyms", []),
            related_terms=data.get("related_terms", []),
            grammatical_info=data.get("grammatical_info", {}),
            license=data.get("license", "CC-BY-4.0"),
            contributor=data.get("contributor"),
            match_type=data.get("match_type", "exact"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary representation."""
        return asdict(self)

    def __str__(self) -> str:
        roman_part = f" ({self.word_roman})" if self.word_roman else ""
        dev_part = f" / {self.word_devanagari}" if self.word_devanagari else ""
        ipa_part = f" [IPA: {self.pronunciation.get('ipa')}]" if self.pronunciation.get("ipa") else ""
        return (
            f"[{self.id}] {self.word}{roman_part}{dev_part}{ipa_part} "
            f"({self.pos}{', ' + self.gender if self.gender else ''}): "
            f"EN: '{self.meaning_en}' | HI: '{self.meaning_hi}' | UR: '{self.meaning_ur}' "
            f"[{self.verification_status}]"
        )


def _build_entry_cache() -> List[DictionaryEntry]:
    """Parse and instantiate all entries."""
    raw_entries = load_dictionary_entries()
    return [DictionaryEntry.from_dict(e) for e in raw_entries]


def lookup(
    word: str,
    script: Optional[str] = None,
    dialect: Optional[str] = None,
) -> Optional[DictionaryEntry]:
    """Look up a single word in the Gojri dictionary.

    Matches across Perso-Arabic, Devanagari, Romanized spellings, and alternative spellings.

    Args:
        word: The word or lemma to look up.
        script: Optional script constraint.
        dialect: Optional dialect constraint.

    Returns:
        The matched DictionaryEntry, or None if not found.
    """
    matches = lookup_all(word, dialect=dialect)
    return matches[0] if matches else None


def lookup_all(
    word: str,
    dialect: Optional[str] = None,
) -> List[DictionaryEntry]:
    """Return all dictionary entries matching the given word across scripts and variants.

    Args:
        word: The word to look up.
        dialect: Optional dialect filter.

    Returns:
        List of matching DictionaryEntry objects.
    """
    if not word or not word.strip():
        return []

    entries = _build_entry_cache()
    target_norm = normalize_for_search(word)
    target_clean = strip_diacritics(normalize(word).casefold())

    matches: List[DictionaryEntry] = []

    for entry in entries:
        if dialect and entry.dialect.lower() != dialect.lower() and entry.dialect != "general":
            continue

        matched = False

        # Match against main word forms
        forms_to_check = [entry.word, entry.word_devanagari or "", entry.word_roman or ""]
        forms_to_check.extend(entry.alternative_spellings)

        for f in forms_to_check:
            if not f:
                continue
            f_norm = normalize_for_search(f)
            f_clean = strip_diacritics(normalize(f).casefold())
            if target_norm == f_norm or target_clean == f_clean:
                matched = True
                break

        if matched:
            entry_copy = DictionaryEntry.from_dict(entry.to_dict())
            entry_copy.match_type = "exact"
            matches.append(entry_copy)

    return matches


def find_synonyms(word: str) -> List[str]:
    """Find documented synonyms for a verified Gojri word.

    Args:
        word: Gojri word.

    Returns:
        List of synonyms.
    """
    entry = lookup(word)
    if entry and entry.synonyms:
        return list(entry.synonyms)

    # Reverse lookup: check if any other entry lists this word as a synonym
    syns: List[str] = []
    norm = normalize_for_search(word)
    for e in _build_entry_cache():
        for s in e.synonyms:
            if normalize_for_search(s) == norm:
                syns.append(e.word)
                if e.word_roman:
                    syns.append(e.word_roman)
    return sorted(list(set(syns)))


def get_word_details(entry_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full linguistic and lexicographical details for an entry ID.

    Args:
        entry_id: Unique entry identifier (e.g. 'word_001').

    Returns:
        Dictionary of complete entry details, or None.
    """
    clean_id = entry_id.strip().lower()
    for entry in _build_entry_cache():
        if entry.id.lower() == clean_id:
            return entry.to_dict()
    return None


def get_word_variants(word: str) -> Dict[str, List[str]]:
    """Get all documented orthographic, regional, and script variants of a word.

    Args:
        word: Input word.

    Returns:
        Dictionary containing alternative spellings, Roman, Devanagari, and dialect notes.
    """
    entry = lookup(word)
    if not entry:
        return {"alternative_spellings": [], "scripts": [], "related_terms": []}

    scripts = []
    if entry.word:
        scripts.append(f"perso-arabic: {entry.word}")
    if entry.word_roman:
        scripts.append(f"roman: {entry.word_roman}")
    if entry.word_devanagari:
        scripts.append(f"devanagari: {entry.word_devanagari}")

    return {
        "headword": [entry.word],
        "alternative_spellings": list(entry.alternative_spellings),
        "scripts": scripts,
        "related_terms": list(entry.related_terms),
        "dialect": [entry.dialect],
    }


def search(
    query: str,
    language: str = "all",
    pos: Optional[str] = None,
    dialect: Optional[str] = None,
    limit: Optional[int] = None,
    fuzzy: bool = False,
    prefix: bool = False,
) -> List[DictionaryEntry]:
    """Search for entries in the dictionary matching a query string.

    Supports exact substring, prefix search, and Levenshtein fuzzy search.

    Args:
        query: Search term (word or meaning).
        language: Field to search ('all', 'english', 'en', 'hindi', 'hi',
                  'urdu', 'ur', 'gojri').
        pos: Optional part of speech filter.
        dialect: Optional dialect filter.
        limit: Maximum number of matching entries to return.
        fuzzy: If True, allows approximate string matching.
        prefix: If True, matches words starting with query prefix.

    Returns:
        List of matching DictionaryEntry objects.
    """
    if not query or not query.strip():
        return []

    entries = _build_entry_cache()
    q_norm = normalize_for_search(query)
    lang_clean = language.strip().lower()

    results: List[DictionaryEntry] = []

    for entry in entries:
        if pos and entry.pos.lower() != pos.lower():
            continue
        if dialect and entry.dialect.lower() != dialect.lower() and entry.dialect != "general":
            continue

        matched = False
        m_type = "exact"

        words_to_check: List[str] = []
        if lang_clean in ("all", "gojri"):
            words_to_check.extend([
                normalize_for_search(entry.word),
                normalize_for_search(entry.word_devanagari or ""),
                normalize_for_search(entry.word_roman or ""),
            ])
            for alt in entry.alternative_spellings:
                words_to_check.append(normalize_for_search(alt))

        meanings_to_check: List[str] = []
        if lang_clean in ("all", "english", "en"):
            meanings_to_check.append(normalize_for_search(entry.meaning_en))
            for d in entry.definitions:
                meanings_to_check.append(normalize_for_search(d))
        if lang_clean in ("all", "hindi", "hi"):
            meanings_to_check.append(normalize_for_search(entry.meaning_hi))
        if lang_clean in ("all", "urdu", "ur"):
            meanings_to_check.append(normalize_for_search(entry.meaning_ur))

        candidates = [w for w in (words_to_check + meanings_to_check) if w]

        # 1. Exact match / substring
        if any(q_norm in c for c in candidates):
            matched = True
            m_type = "exact"

        # 2. Prefix search
        elif prefix and any(c.startswith(q_norm) for c in candidates):
            matched = True
            m_type = "prefix"

        # 3. Fuzzy search (Levenshtein distance)
        elif fuzzy:
            max_dist = max(1, len(q_norm) // 3)
            for c in candidates:
                # Compare full tokens
                for tok in c.split():
                    if abs(len(tok) - len(q_norm)) <= max_dist:
                        dist = _levenshtein_distance(q_norm, tok)
                        if dist <= max_dist:
                            matched = True
                            m_type = "fuzzy"
                            break
                if matched:
                    break

        if matched:
            entry_copy = DictionaryEntry.from_dict(entry.to_dict())
            entry_copy.match_type = m_type
            results.append(entry_copy)
            if limit is not None and len(results) >= limit:
                break

    return results
