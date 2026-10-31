"""Text normalization and script detection for Gojri language texts.

Supports extended Perso-Arabic (Urdu/Nastaliq style), Devanagari, and
academic Romanized transcriptions.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Literal, Tuple, Union, overload


# Arabic / Perso-Arabic diacritics (tashkeel / harakat)
ARABIC_DIACRITICS_REGEX = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]"
)

# Arabic character normalization map (normalize non-standard variants to standard Urdu/Gojri forms)
PERSO_ARABIC_CHAR_MAP = {
    # Alif variants -> standard Alif
    "\u0622": "\u0627",  # Madda -> Alif (for loose search matching)
    "\u0623": "\u0627",  # Hamza on Alif
    "\u0625": "\u0627",  # Hamza below Alif
    "\u0671": "\u0627",  # Alif Wasla
    # Kaf variants -> Urdu Keheh
    "\u0643": "\u06A9",  # Arabic Kaf -> Persian/Urdu Kaf
    # Yeh variants -> Urdu Yeh / Bari Ye
    "\u064A": "\u06CC",  # Arabic Yeh -> Farsi/Urdu Yeh
    "\u0649": "\u06CC",  # Alef Maksura -> Urdu Yeh
    # Teh Marbuta -> Heh / Teh
    "\u0629": "\u06C1",  # Teh Marbuta -> Urdu Heh Goal
    "\u0647": "\u06C1",  # Arabic Ha -> Urdu Heh Goal (for consistency)
    # Waw variants
    "\u0624": "\u0648",  # Waw with Hamza
}

# Devanagari combining marks for diacritic stripping
DEV_COMBINING_MARKS = re.compile(r"[\u0901-\u0903\u093C\u093E-\u094F\u0951-\u0957\u0962-\u0963]")


def detect_script(text: str) -> str:
    """Detect the predominant script of a given text.

    Returns one of:
      - 'perso-arabic'
      - 'devanagari'
      - 'latin'
      - 'mixed'
      - 'unknown'

    Args:
        text: Input text string.

    Returns:
        String name of the detected script.
    """
    if not text or not text.strip():
        return "unknown"

    counts = {"perso-arabic": 0, "devanagari": 0, "latin": 0}

    for ch in text:
        cp = ord(ch)
        # Perso-Arabic Unicode ranges (Arabic, Arabic Supplement, Arabic Extended)
        if (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F) or (0x08A0 <= cp <= 0x08FF):
            counts["perso-arabic"] += 1
        # Devanagari Unicode range
        elif 0x0900 <= cp <= 0x097F:
            counts["devanagari"] += 1
        # Latin Unicode ranges (Basic Latin, Latin-1 Supplement, Latin Extended A/B)
        elif (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F):
            counts["latin"] += 1

    total = sum(counts.values())
    if total == 0:
        return "unknown"

    # If one script accounts for more than 75% of classified letters, assign it
    for script_name, count in counts.items():
        if count / total >= 0.75:
            return script_name

    # Check if multiple non-trivial scripts are present
    active_scripts = [s for s, c in counts.items() if c > 0]
    if len(active_scripts) > 1:
        return "mixed"

    return "unknown"


def strip_diacritics(text: str, script: str | None = None) -> str:
    """Remove combining diacritics and harakat/tashkeel from text.

    Args:
        text: Text from which to strip diacritics.
        script: Optional script hint ('perso-arabic', 'devanagari', 'latin').
                If None, auto-detected or applied generally.

    Returns:
        Text with combining marks removed.
    """
    if not text:
        return ""

    if script is None:
        script = detect_script(text)

    if script == "perso-arabic":
        return ARABIC_DIACRITICS_REGEX.sub("", text)
    elif script == "devanagari":
        # Strip nukta and accents but retain essential matras if basic stripping
        return re.sub(r"[\u093C\u0951-\u0954]", "", text)
    elif script == "latin":
        # Decompose, strip non-spacing marks, recompose
        decomposed = unicodedata.normalize("NFD", text)
        filtered = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
        return unicodedata.normalize("NFC", filtered)
    else:
        # Generic removal across scripts
        step1 = ARABIC_DIACRITICS_REGEX.sub("", text)
        decomposed = unicodedata.normalize("NFD", step1)
        filtered = "".join(
            ch for ch in decomposed if unicodedata.category(ch) != "Mn" or ord(ch) in (0x093C,)
        )
        return unicodedata.normalize("NFC", filtered)


UnicodeNormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]


@overload
def normalize(
    text: str,
    remove_diacritics: bool = False,
    preserve_original: Literal[False] = False,
    normalize_unicode: UnicodeNormalizationForm = "NFC",
) -> str:
    ...


@overload
def normalize(
    text: str,
    remove_diacritics: bool = False,
    preserve_original: Literal[True] = True,
    normalize_unicode: UnicodeNormalizationForm = "NFC",
) -> Tuple[str, str]:
    ...


@overload
def normalize(
    text: str,
    remove_diacritics: bool = False,
    preserve_original: bool = False,
    normalize_unicode: UnicodeNormalizationForm = "NFC",
) -> Union[str, Tuple[str, str]]:
    ...


def normalize(
    text: str,
    remove_diacritics: bool = False,
    preserve_original: bool = False,
    normalize_unicode: UnicodeNormalizationForm = "NFC",
) -> Union[str, Tuple[str, str]]:
    """Normalize Gojri text across script variations, whitespace, and Unicode forms.

    Args:
        text: Input string.
        remove_diacritics: If True, strips diacritical marks (harakat/accents).
        preserve_original: If True, returns a tuple of (normalized_text, original_text).
        normalize_unicode: Unicode normalization form ('NFC', 'NFKC', 'NFD', 'NFKD').

    Returns:
        Normalized string, or tuple of (normalized, original) if preserve_original=True.
    """
    if text is None:
        return ("", text) if preserve_original else ""

    original = text

    # Step 1: Unicode normalization
    valid_forms: Tuple[UnicodeNormalizationForm, ...] = ("NFC", "NFD", "NFKC", "NFKD")
    form: UnicodeNormalizationForm = (
        normalize_unicode if normalize_unicode in valid_forms else "NFC"
    )
    normalized = unicodedata.normalize(form, text)

    # Step 2: Normalize standard whitespace (collapse tabs, newlines, multiple spaces)
    normalized = re.sub(r"[ \t\r\f\v]+", " ", normalized)
    normalized = normalized.strip()

    # Step 3: Normalize common typography across scripts
    # Standardize Persian/Arabic punctuation variants to regular text or vice versa
    normalized = normalized.replace("“", '"').replace("”", '"')
    normalized = normalized.replace("‘", "'").replace("’", "'")

    # Step 4: Optional diacritic removal
    if remove_diacritics:
        script = detect_script(normalized)
        normalized = strip_diacritics(normalized, script)

    if preserve_original:
        return (normalized, original)
    return normalized


def normalize_spelling(text: str) -> str:
    """Standardize common spelling variations and character encoding ambiguities in Gojri.

    Standardizes Arabic Kaf (ك) to Persian/Urdu Keheh (ک), Arabic Yeh (ي, ى) to
    Urdu Yeh (ی), Arabic Ha (ه) to Urdu Goal Heh (ہ), and consolidates aspirated consonants
    with proper do-chashmi heh (ھ).

    Args:
        text: Input string.

    Returns:
        Spelling-normalized string.
    """
    if not text:
        return ""

    out = text
    # Standardize character encodings
    for non_std, std in PERSO_ARABIC_CHAR_MAP.items():
        if non_std != "\u0622":  # Preserve Alif Madda in spelling
            out = out.replace(non_std, std)

    # Standardize aspiration to proper do-chashmi heh
    aspiration_pairs = [
        ("کہ", "کھ"),
        ("گہ", "گھ"),
        ("بہ", "بھ"),
        ("پہ", "پھ"),
        ("تہ", "تھ"),
        ("ٹہ", "ٹھ"),
        ("جہ", "جھ"),
        ("چہ", "چھ"),
        ("دہ", "دھ"),
        ("ڈہ", "ڈھ"),
        ("ڑہ", "ڑھ"),
    ]
    for non_do, do_chashmi in aspiration_pairs:
        out = out.replace(non_do, do_chashmi)

    return normalize(out)


def normalize_for_search(text: str) -> str:
    """Aggressively normalize a text or query string for index search matching.

    Performs case-folding, diacritic stripping, script-specific character
    unifications (e.g. Alif Madda -> Alif, Arabic Kaf -> Persian Kaf),
    and punctuation removal.

    Args:
        text: Query or word string.

    Returns:
        Normalized search key.
    """
    if not text:
        return ""

    # NFC baseline
    norm = unicodedata.normalize("NFC", text.strip())

    # Lowercase Latin characters
    norm = norm.casefold()

    # Apply Perso-Arabic character mappings
    chars = [PERSO_ARABIC_CHAR_MAP.get(ch, ch) for ch in norm]
    norm = "".join(chars)

    # Strip diacritics
    norm = strip_diacritics(norm)

    # Strip punctuation and symbols across all scripts (including Arabic comma \u060C, full stop \u06D4, etc.)
    norm = "".join(
        ch for ch in norm
        if not unicodedata.category(ch).startswith("P")
        and not unicodedata.category(ch).startswith("S")
    )
    norm = re.sub(r"\s+", " ", norm).strip()

    return norm
