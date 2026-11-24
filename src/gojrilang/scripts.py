"""Comprehensive script and orthographic management subsystem for Gojri.

Unifies script identification, Unicode normalization, reversible transliteration,
diacritic management, and RTL text handling across Extended Perso-Arabic,
Devanagari, and Academic Roman writing standards.
"""

from __future__ import annotations

import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from gojrilang.normalize import (
    detect_script as _detect_script,
    normalize as _normalize,
    normalize_for_search,
    normalize_spelling,
    strip_diacritics as _strip_diacritics,
)
from gojrilang.transliteration import (
    romanize as _romanize,
    supported_transliteration_pairs,
    transliterate as _transliterate,
)

SUPPORTED_SCRIPTS: Set[str] = {"perso-arabic", "devanagari", "roman"}


def detect_script(text: str) -> str:
    """Detect writing script of Gojri text (perso-arabic, devanagari, or roman)."""
    return _detect_script(text)


def normalize(
    text: str,
    form: str = "NFC",
    strip_extra_whitespace: bool = True,
    preserve_original: bool = False,
) -> str:
    """Normalize Gojri text with Unicode standardization and optional whitespace cleanup."""
    return _normalize(
        text,
        form=form,
        strip_extra_whitespace=strip_extra_whitespace,
        preserve_original=preserve_original,
    )


def strip_diacritics(text: str) -> str:
    """Remove Arabic/Urdu harakat, Devanagari vowel signs, or Latin diacritics."""
    return _strip_diacritics(text)


def transliterate(
    text: str,
    source_script: Optional[str] = None,
    target_script: str = "roman",
) -> str:
    """Transliterate text between supported Gojri scripts."""
    return _transliterate(text, source_script=source_script, target_script=target_script)


def romanize(text: str, scheme: str = "academic") -> str:
    """Convert Gojri text in Perso-Arabic or Devanagari to Roman transliteration."""
    return _romanize(text, scheme=scheme)


def is_rtl(text: str) -> bool:
    """Check if the text primarily uses a right-to-left writing system (Perso-Arabic)."""
    if not text or not text.strip():
        return False
    arabic_count = sum(1 for c in text if "\u0600" <= c <= "\u08FF" or "\uFB50" <= c <= "\uFDFF" or "\uFE70" <= c <= "\uFEFF")
    return arabic_count > (len(text.replace(" ", "")) * 0.3)


def get_supported_scripts() -> List[str]:
    """Return all documented Gojri writing scripts."""
    return sorted(list(SUPPORTED_SCRIPTS))


def get_supported_script_pairs() -> List[Tuple[str, str]]:
    """Return all validated bidirectional transliteration pairs."""
    return supported_transliteration_pairs()
