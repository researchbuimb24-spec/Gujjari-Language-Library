"""Vocabulary classification, lexical tiers, and headword management for Gojri."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from gojrilang.datasets import load_dictionary_entries
from gojrilang.dictionary import lookup


def get_vocabulary_summary() -> Dict[str, Any]:
    """Return structured breakdown of verified vocabulary by POS, semantic tier, and script."""
    entries = load_dictionary_entries()
    pos_counts: Dict[str, int] = {}
    dialect_counts: Dict[str, int] = {}
    verified_count = 0

    for e in entries:
        pos = e.get("pos", "unknown")
        pos_counts[pos] = pos_counts.get(pos, 0) + 1
        dial = e.get("dialect", "General")
        dialect_counts[dial] = dialect_counts.get(dial, 0) + 1
        if e.get("verification_status") == "verified":
            verified_count += 1

    return {
        "total_headwords": len(entries),
        "total_headwords_count": len(entries),
        "verified_headwords": verified_count,
        "verified_headwords_count": verified_count,
        "parts_of_speech": pos_counts,
        "dialects": dialect_counts,
        "semantic_domains": [
            "colors", "anatomy", "kinship", "livestock", "seasons",
            "celestial", "hydrology", "household", "pastoral_tools",
            "verbs", "music", "literature", "ethics"
        ],
    }


def list_headwords(pos: Optional[str] = None, dialect: Optional[str] = None) -> List[str]:
    """List canonical dictionary headwords, optionally filtered by POS or dialect."""
    entries = load_dictionary_entries()
    headwords: List[str] = []
    for e in entries:
        if pos and e.get("pos", "").lower() != pos.strip().lower():
            continue
        if dialect and dialect.strip().lower() not in e.get("dialect", "").lower():
            continue
        headwords.append(e.get("word", ""))
    return headwords


def classify_word(word: str) -> Dict[str, Any]:
    """Classify a given word into headword, inflected form, or unknown with linguistic details."""
    clean = word.strip()
    exact = lookup(clean)
    if exact:
        return {
            "word": clean,
            "status": "headword",
            "pos": exact.pos,
            "meaning_en": exact.meaning_en,
            "meaning_hi": exact.meaning_hi,
            "meaning_ur": exact.meaning_ur,
            "is_inflected": False,
        }

    from gojrilang.morphology import analyze_word
    analysis = analyze_word(clean)
    if analysis.is_inflected:
        return {
            "word": clean,
            "status": "inflected_form",
            "root": analysis.root,
            "category": analysis.category,
            "affixes": analysis.affixes_found,
            "is_inflected": True,
        }

    return {
        "word": clean,
        "status": "unindexed",
        "is_inflected": False,
    }
