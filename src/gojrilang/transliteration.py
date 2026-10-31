"""Transliteration engine for Gojri language texts.

Provides validated script conversion between Gojri's primary written forms:
- Extended Perso-Arabic (Urdu / Nastaliq-based)
- Devanagari (adapted for Gojri)
- Academic Roman / Latin (ISO/phonological transcription)

Unvalidated or speculative script conversions raise UnsupportedTransliterationError.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Dict, List, Tuple

from gojrilang.exceptions import UnsupportedScriptError, UnsupportedTransliterationError
from gojrilang.normalize import detect_script, normalize

# Standard script identifiers
SCRIPT_CANONICAL = {
    "perso-arabic": "perso-arabic",
    "perso_arabic": "perso-arabic",
    "persoarabic": "perso-arabic",
    "urdu": "perso-arabic",
    "nastaliq": "perso-arabic",
    "shahmukhi": "perso-arabic",
    "devanagari": "devanagari",
    "hindi": "devanagari",
    "dev": "devanagari",
    "roman": "roman",
    "latin": "roman",
    "english": "roman",
    "iast": "roman",
}

SUPPORTED_CANONICAL_SCRIPTS = {"perso-arabic", "devanagari", "roman"}

_RULES_CACHE: Dict[str, Dict[str, str]] | None = None


def _load_rules() -> Dict[str, Dict[str, str]]:
    """Load validated transliteration tables from package data."""
    global _RULES_CACHE
    if _RULES_CACHE is not None:
        return _RULES_CACHE

    ref = resources.files("gojrilang.data").joinpath("transliteration_rules.json")
    with ref.open("r", encoding="utf-8") as f:
        data = json.load(f)

    _RULES_CACHE = {
        "perso_arabic_to_roman": data.get("perso_arabic_to_roman", {}),
        "devanagari_to_roman": data.get("devanagari_to_roman", {}),
        "roman_to_devanagari": data.get("roman_to_devanagari", {}),
        "roman_to_perso_arabic": data.get("roman_to_perso_arabic", {}),
    }
    return _RULES_CACHE


def _normalize_script_name(script: str) -> str:
    """Normalize input script name to canonical format or raise error."""
    clean = script.strip().lower()
    canonical = SCRIPT_CANONICAL.get(clean)
    if not canonical:
        raise UnsupportedScriptError(script, supported=sorted(list(SUPPORTED_CANONICAL_SCRIPTS)))
    return canonical


def supported_transliteration_pairs() -> List[Tuple[str, str]]:
    """Return the list of validated script conversion pairs."""
    return [
        ("perso-arabic", "roman"),
        ("roman", "perso-arabic"),
        ("devanagari", "roman"),
        ("roman", "devanagari"),
        ("perso-arabic", "devanagari"),
        ("devanagari", "perso-arabic"),
    ]


# Independent Devanagari vowels to combining vowel signs (matras)
DEV_VOWEL_TO_MATRA = {
    "अ": "",
    "आ": "\u093E",  # ा
    "इ": "\u093F",  # ि
    "ई": "\u0940",  # ी
    "उ": "\u0941",  # ु
    "ऊ": "\u0942",  # ू
    "ए": "\u0947",  # े
    "ऐ": "\u0948",  # ै
    "ओ": "\u094B",  # ो
    "औ": "\u094C",  # ौ
}


def _is_devanagari_consonant_or_nukta(ch: str) -> bool:
    cp = ord(ch)
    return (0x0915 <= cp <= 0x0939) or (0x0958 <= cp <= 0x095F) or cp in (0x0933, 0x093C)


def _compose_devanagari_matras(text: str) -> str:
    """Convert independent vowels into matras when preceded by consonants."""
    out: List[str] = []
    for ch in text:
        if ch in DEV_VOWEL_TO_MATRA and out and _is_devanagari_consonant_or_nukta(out[-1]):
            out.append(DEV_VOWEL_TO_MATRA[ch])
        else:
            out.append(ch)
    return "".join(out)


def _map_tokens(text: str, table: Dict[str, str]) -> str:
    """Greedily transliterate text using a token table ordered by pattern length."""
    sorted_keys = sorted(table.keys(), key=len, reverse=True)
    result: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        matched = False
        for k in sorted_keys:
            if text.startswith(k, i):
                result.append(table[k])
                i += len(k)
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1

    return "".join(result)


def transliterate(
    text: str,
    source: str | None = None,
    target: str = "roman",
) -> str:
    """Transliterate Gojri text between validated scripts.

    Supported scripts: 'perso-arabic', 'devanagari', 'roman'.

    Args:
        text: Input text string.
        source: Source script name. If None, auto-detected.
        target: Target script name ('perso-arabic', 'devanagari', 'roman').

    Returns:
        Transliterated string.

    Raises:
        UnsupportedScriptError: If source or target is unrecognised.
        UnsupportedTransliterationError: If the script pair lacks validated rules.
    """
    if not text:
        return ""

    if source is None:
        detected = detect_script(text)
        if detected in ("unknown", "mixed"):
            raise UnsupportedScriptError(
                detected,
                supported=sorted(list(SUPPORTED_CANONICAL_SCRIPTS)),
            )
        source = detected

    src_can = _normalize_script_name(source)
    tgt_can = _normalize_script_name(target)

    if src_can == tgt_can:
        return normalize(text)

    rules = _load_rules()
    normalized_input = normalize(text)

    # 1. Direct Perso-Arabic -> Roman
    if src_can == "perso-arabic" and tgt_can == "roman":
        return _map_tokens(normalized_input, rules["perso_arabic_to_roman"])

    # 2. Direct Devanagari -> Roman
    if src_can == "devanagari" and tgt_can == "roman":
        return _map_tokens(normalized_input, rules["devanagari_to_roman"])

    # 3. Direct Roman -> Perso-Arabic
    if src_can == "roman" and tgt_can == "perso-arabic":
        return _map_tokens(normalized_input.lower(), rules["roman_to_perso_arabic"])

    # 4. Direct Roman -> Devanagari
    if src_can == "roman" and tgt_can == "devanagari":
        raw_dev = _map_tokens(normalized_input.lower(), rules["roman_to_devanagari"])
        return _compose_devanagari_matras(raw_dev)

    # 5. Perso-Arabic -> Devanagari (via validated Roman phonemic bridge)
    if src_can == "perso-arabic" and tgt_can == "devanagari":
        roman_inter = _map_tokens(normalized_input, rules["perso_arabic_to_roman"])
        raw_dev = _map_tokens(roman_inter.lower(), rules["roman_to_devanagari"])
        return _compose_devanagari_matras(raw_dev)

    # 6. Devanagari -> Perso-Arabic (via validated Roman phonemic bridge)
    if src_can == "devanagari" and tgt_can == "perso-arabic":
        roman_inter = _map_tokens(normalized_input, rules["devanagari_to_roman"])
        return _map_tokens(roman_inter.lower(), rules["roman_to_perso_arabic"])

    raise UnsupportedTransliterationError(
        source_script=src_can,
        target_script=tgt_can,
        reason="Direct conversion path has not been scientifically validated.",
    )


IPA_REPLACEMENTS = {
    "gh": "ɡʱ", "kh": "kʰ", "jh": "d͡ʒʱ", "chh": "t͡ʃʰ",
    "dh": "d̪ʱ", "th": "t̪ʰ", "bh": "bʱ", "ph": "pʰ",
    "ṭh": "ʈʰ", "ḍh": "ɖʱ", "ṛh": "ɽʱ",
    "sh": "ʃ", "zh": "ʒ",
    "ā": "aː", "ī": "iː", "ū": "uː", "e": "eː", "o": "oː",
    "ṭ": "ʈ", "ḍ": "ɖ", "ṛ": "ɽ", "ṇ": "ɳ", "ḷ": "ɭ",
    "ñ": "̃", "ch": "t͡ʃ", "j": "d͡ʒ",
}


def romanize(text: str, scheme: str = "academic") -> str:
    """Romanize Gojri text into a requested transcription scheme.

    Supported schemes:
      - 'academic' (default): CIIL/SIL phonological transcription with macrons & underdots (e.g. 'ghoṛo', 'pāṇi')
      - 'simple' / 'simple_roman': Plain ASCII without diacritical marks (e.g. 'ghoro', 'pani')
      - 'ipa': International Phonetic Alphabet representation (e.g. 'ɡʱoːɽoː')

    Args:
        text: Input text string in Perso-Arabic, Devanagari, or Roman.
        scheme: Transcription scheme.

    Returns:
        Romanized text string.
    """
    if not text:
        return ""

    academic_roman = transliterate(text, target="roman")

    scheme_clean = scheme.strip().lower()
    if scheme_clean == "academic":
        return academic_roman
    elif scheme_clean in ("simple", "simple_roman", "ascii"):
        from gojrilang.normalize import strip_diacritics
        return strip_diacritics(academic_roman, script="latin")
    elif scheme_clean == "ipa":
        sorted_keys = sorted(IPA_REPLACEMENTS.keys(), key=len, reverse=True)
        res = academic_roman.lower()
        for k in sorted_keys:
            res = res.replace(k, IPA_REPLACEMENTS[k])
        return f"/{res}/"

    raise UnsupportedTransliterationError(
        source_script=detect_script(text),
        target_script=scheme,
        reason=f"Unknown romanization scheme '{scheme}'. Supported: 'academic', 'simple', 'ipa'.",
    )
