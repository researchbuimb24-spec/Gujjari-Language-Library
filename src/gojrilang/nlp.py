"""Computational linguistics and natural language processing toolkit for Gojri.

Provides tokenization, sentence segmentation, rule-assisted baseline POS tagging,
n-gram analysis, spell-checking suggestions, text similarity, and language identification
designed specifically for Gojri (ISO 639-3: gju) across Perso-Arabic, Devanagari, and Roman scripts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from gojrilang.dictionary import lookup
from gojrilang.morphology import lemmatize
from gojrilang.normalize import detect_script, normalize_for_search, strip_diacritics

# Distinctive Gojri punctuation marks and sentence terminators
_SENT_END_REGEX = re.compile(r"([۔।॥\.\?!؟\n]+)")
_PUNCT_CHARS = r",\.;:!\?۔।॥\(\)\[\]\{\}\"\'«»`~@#\$%\^&\*_\-+=\\\|/<>،؛؟\u060C\u061B\u061F\u06D4\u0964\u0965"
_WORD_REGEX = re.compile(rf"[^\s{_PUNCT_CHARS}]+|[{_PUNCT_CHARS}]")

# Distinctive grammatical markers for baseline POS tagging
_GOJRI_POSTPOSITIONS: Set[str] = {
    "رو", "ری", "را", "رے", "رو", "کا", "کی", "کے", "نا", "نے", "ما", "توں", "تھے", "کنے", "وال", "نال",
    "रो", "री", "रा", "रे", "का", "की", "के", "ना", "ने", "मा", "तों", "थे", "कने", "वाल", "नाल",
    "ro", "rī", "rā", "re", "nā", "ne", "mā", "tõ", "kane", "vāl", "nāl",
}

_GOJRI_PRONOUNS: Set[str] = {
    "ہک", "ہوں", "میں", "تو", "توں", "اوہ", "ایہہ", "اس", "انھاں", "اساں", "تساں", "اپݨو", "اپݨی", "اپݨا", "جیہڑو", "سو", "کی", "کون",
    "हिक", "हूँ", "मैं", "तू", "तूँ", "ओह", "एह", "उस", "इन्हाँ", "असाँ", "तुसाँ", "अपणो", "अपणी", "अपणा", "जेहड़ो", "सो", "की", "कौन",
    "hik", "hū̃", "maĩ", "tū", "tū̃", "oh", "eh", "us", "inhā̃", "asā̃", "tusā̃", "apṇo", "apṇī", "apṇā", "jehṛo", "so", "kī", "kaun",
}

_GOJRI_AUXILIARIES: Set[str] = {
    "ہے", "ہن", "نہیں", "سی", "سن", "تھیا", "تھیو", "ہووے", "ہوسی", "چھوں", "چھو", "چھاتے",
    "है", "हन", "नहीं", "सी", "सन", "थिया", "थियो", "होवे", "होसी", "छूँ", "छो", "छाते",
    "hai", "han", "nahī̃", "sī", "san", "thiyā", "thiyo", "hove", "hosī", "chhū̃", "chho",
}

_GOJRI_CONJUNCTIONS: Set[str] = {
    "تے", "اتے", "یا", "کہ", "پر", "جے", "تاں", "کیونکہ",
    "ते", "अते", "या", "कि", "पर", "जे", "ताँ", "क्योंकि",
    "te", "ate", "yā", "ki", "par", "je", "tā̃", "kyūṅki",
}


def tokenize(text: str, preserve_punctuation: bool = True) -> List[str]:
    """Tokenize Gojri text into words and punctuation tokens."""
    if not text or not text.strip():
        return []
    raw_tokens = _WORD_REGEX.findall(text)
    if preserve_punctuation:
        return [t.strip() for t in raw_tokens if t.strip()]
    return [t.strip() for t in raw_tokens if t.strip() and not re.match(rf"^[{_PUNCT_CHARS}]+$", t)]


def sent_tokenize(text: str) -> List[str]:
    """Segment Gojri text into individual sentences based on terminators (۔, ।, ., ?, !)."""
    if not text or not text.strip():
        return []
    parts = _SENT_END_REGEX.split(text.strip())
    sentences: List[str] = []
    current = ""
    for p in parts:
        if _SENT_END_REGEX.match(p):
            current += p
            if current.strip():
                sentences.append(current.strip())
            current = ""
        else:
            current += p
    if current.strip():
        sentences.append(current.strip())
    return sentences


def pos_tag(tokens_or_text: Union[str, List[str]]) -> List[Tuple[str, str]]:
    """Rule-assisted baseline part-of-speech tagger for Gojri."""
    tokens = tokenize(tokens_or_text) if isinstance(tokens_or_text, str) else tokens_or_text
    tagged: List[Tuple[str, str]] = []

    for tok in tokens:
        clean = tok.strip()
        if not clean:
            continue

        # Punctuation check
        if re.match(r"^[^\w\s]+$", clean):
            tagged.append((clean, "PUNCT"))
            continue

        # Digits check
        if clean.isdigit() or re.match(r"^[\u0660-\u0669\u06F0-\u06F9\u0966-\u096F]+$", clean):
            tagged.append((clean, "NUM"))
            continue

        tok_lower = clean.lower()

        # Dictionary lookup for attested POS
        entry = lookup(clean)
        if entry and entry.pos:
            pos_val = entry.pos.upper()
            if pos_val == "POSTPOSITION":
                pos_val = "POSTPOS"
            tagged.append((clean, pos_val))
            continue

        # Grammatical functional words
        if clean in _GOJRI_POSTPOSITIONS or tok_lower in _GOJRI_POSTPOSITIONS:
            tagged.append((clean, "POSTPOS"))
        elif clean in _GOJRI_PRONOUNS or tok_lower in _GOJRI_PRONOUNS:
            tagged.append((clean, "PRON"))
        elif clean in _GOJRI_AUXILIARIES or tok_lower in _GOJRI_AUXILIARIES:
            tagged.append((clean, "AUX"))
        elif clean in _GOJRI_CONJUNCTIONS or tok_lower in _GOJRI_CONJUNCTIONS:
            tagged.append((clean, "CONJ"))
        # Morphological verb endings: infinitives (-ṇo, -vṇo), participles (-to, -do)
        elif clean.endswith(("وݨو", "ݨو", "णो", "वणो", "to", "do", "ṇo", "vṇo")):
            tagged.append((clean, "VERB"))
        # Marked masculine nouns/adjectives in -o / -ā
        elif clean.endswith(("و", "ओ", "ो", "o", "a")):
            tagged.append((clean, "NOUN"))
        # Marked feminine nouns/adjectives in -ī
        elif clean.endswith(("ی", "ई", "ी", "ī", "i")):
            tagged.append((clean, "NOUN"))
        else:
            tagged.append((clean, "NOUN"))

    return tagged


def get_ngrams(tokens_or_text: Union[str, List[str]], n: int = 2) -> List[Tuple[str, ...]]:
    """Extract word n-grams from Gojri text or token sequence."""
    tokens = tokenize(tokens_or_text, preserve_punctuation=False) if isinstance(tokens_or_text, str) else tokens_or_text
    if len(tokens) < n or n < 1:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute standard Levenshtein edit distance."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev[j + 1] + 1
            deletions = curr[j] + 1
            substitutions = prev[j] + (c1 != c2)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]


def spell_check(word: str, max_suggestions: int = 5) -> Dict[str, Any]:
    """Check word against verified Gojri vocabulary and offer candidate corrections."""
    clean = word.strip()
    if not clean:
        return {"word": word, "is_correct": False, "suggestions": []}

    # If the word directly exists, it's correct
    exact = lookup(clean)
    if exact:
        return {"word": clean, "is_correct": True, "suggestions": []}

    # Try checking normalized / diacritic-stripped
    norm_w = normalize_for_search(clean)
    from gojrilang.datasets import load_dictionary_entries
    entries = load_dictionary_entries()

    candidates: List[Tuple[int, str]] = []
    for e in entries:
        candidate_word = e.get("word", "")
        cand_norm = normalize_for_search(candidate_word)
        dist = _levenshtein_distance(norm_w, cand_norm)
        if dist <= 2:
            candidates.append((dist, candidate_word))
        # Check alternative spellings
        for alt in e.get("alternative_spellings", []):
            alt_dist = _levenshtein_distance(norm_w, normalize_for_search(alt))
            if alt_dist <= 2:
                candidates.append((alt_dist, alt))
                candidates.append((alt_dist, candidate_word))

    # Sort by minimum edit distance and deduplicate
    candidates.sort(key=lambda x: x[0])
    seen: Set[str] = set()
    suggestions: List[str] = []
    for _, cand in candidates:
        if cand not in seen and cand != clean:
            seen.add(cand)
            suggestions.append(cand)
            if len(suggestions) >= max_suggestions:
                break

    return {
        "word": clean,
        "is_correct": False,
        "suggestions": suggestions,
    }


def text_similarity(text1: str, text2: str, method: str = "jaccard") -> float:
    """Compute linguistic similarity between two Gojri texts (Jaccard or Levenshtein)."""
    if not text1 or not text2:
        return 0.0
    if text1.strip() == text2.strip():
        return 1.0

    if method.lower() == "jaccard":
        tokens1 = set(tokenize(text1.lower(), preserve_punctuation=False))
        tokens2 = set(tokenize(text2.lower(), preserve_punctuation=False))
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)

    # Character-level Levenshtein similarity ratio
    t1_norm = normalize_for_search(text1)
    t2_norm = normalize_for_search(text2)
    max_len = max(len(t1_norm), len(t2_norm))
    if max_len == 0:
        return 1.0
    dist = _levenshtein_distance(t1_norm, t2_norm)
    return max(0.0, 1.0 - (dist / max_len))


def detect_language(text: str) -> Dict[str, Any]:
    """Identify whether text is Gujari / Gojri, Urdu, Hindi, or English."""
    if not text or not text.strip():
        return {"language": "unknown", "confidence": 0.0}

    # Distinctive Gojri diagnostic markers
    gojri_markers = {"ݨ", "ݪ", "چھوں", "تھیا", "رو", "ری", "ما", "کنے", "وال", "छूँ", "थिया", "रो", "री", "कने"}
    found_markers = [m for m in gojri_markers if m in text]
    script = detect_script(text)

    if found_markers:
        return {
            "language": "gojri",
            "iso_code": "gju",
            "confidence": 0.95,
            "detected_script": script,
            "diagnostic_markers": found_markers,
        }

    # Script-based heuristics
    if script == "perso-arabic":
        return {"language": "gojri_or_urdu", "iso_code": "gju/urd", "confidence": 0.70, "detected_script": script}
    elif script == "devanagari":
        return {"language": "gojri_or_hindi", "iso_code": "gju/hin", "confidence": 0.70, "detected_script": script}
    else:
        # Check if ASCII / English
        if all(ord(c) < 128 for c in text if c.isalpha()):
            return {"language": "english", "iso_code": "eng", "confidence": 0.90, "detected_script": "latin"}
        return {"language": "gojri_roman", "iso_code": "gju", "confidence": 0.75, "detected_script": "roman"}


def stem(word: str) -> str:
    """Rule-guided Gojri stemmer stripping documented nominal and verbal inflections."""
    clean = word.strip()
    if len(clean) <= 3:
        return clean

    # Verbal endings: -vaṇo, -ṇa, -ṇī, -ṇe
    for suffix in ("اوݨو", "اوݨا", "اوݨی", "وݨو", "ݨو", "वणो", "वणे", "वणा", "णा", "णी"):
        if clean.endswith(suffix):
            return clean[:-len(suffix)]

    # Nominal plural oblique: -ā̃, -yā̃
    for suffix in ("یاں", "اں", "ियाँ", "ाँ"):
        if clean.endswith(suffix):
            return clean[:-len(suffix)]

    return clean
