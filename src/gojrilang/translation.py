"""Translation interface for Gojri language texts.

Uses verified phrase lexicons and documented dictionary correspondences.
Avoids speculative or hallucinated machine translations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.datasets import load_translation_data_raw
from gojrilang.dictionary import lookup, search
from gojrilang.normalize import normalize, normalize_for_search


SUPPORTED_LANGUAGES = {"gojri", "english", "hindi", "urdu"}

LANG_ALIASES = {
    "gojri": "gojri",
    "gju": "gojri",
    "gujari": "gojri",
    "english": "english",
    "en": "english",
    "eng": "english",
    "hindi": "hindi",
    "hi": "hindi",
    "hin": "hindi",
    "urdu": "urdu",
    "ur": "urdu",
    "urd": "urdu",
}


@dataclass
class TranslationResult:
    """The result of a translation request."""

    text: str
    status: str
    source: str
    target: str
    confidence: float
    matched_phrases: List[Dict[str, Any]]
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.status.upper()}] '{self.text}' (Source: {self.source} -> Target: {self.target})"


def _canonical_lang(lang: str) -> Optional[str]:
    return LANG_ALIASES.get(lang.strip().lower())


def translate(
    text: str,
    source: str = "gojri",
    target: str = "english",
) -> TranslationResult:
    """Translate text between Gojri and supported languages (English, Hindi, Urdu).

    Uses authenticated phrase records and verified dictionary lookups.
    Returns status 'exact_match', 'lexical_match', 'not_found', or 'unsupported_pair'.

    Args:
        text: Input phrase or sentence.
        source: Source language ('gojri', 'english', 'hindi', 'urdu').
        target: Target language ('gojri', 'english', 'hindi', 'urdu').

    Returns:
        TranslationResult instance.
    """
    if not text or not text.strip():
        return TranslationResult(
            text="",
            status="not_found",
            source=source,
            target=target,
            confidence=0.0,
            matched_phrases=[],
            notes="Empty input text.",
        )

    src_can = _canonical_lang(source)
    tgt_can = _canonical_lang(target)

    if not src_can or not tgt_can:
        unrec = source if not src_can else target
        return TranslationResult(
            text=f"Unsupported language '{unrec}'.",
            status="unsupported_pair",
            source=source,
            target=target,
            confidence=0.0,
            matched_phrases=[],
            notes=f"Supported languages: {', '.join(sorted(list(SUPPORTED_LANGUAGES)))}",
        )

    if src_can == tgt_can:
        return TranslationResult(
            text=normalize(text),
            status="exact_match",
            source=src_can,
            target=tgt_can,
            confidence=1.0,
            matched_phrases=[],
            notes="Source and target languages are identical.",
        )

    norm_query = normalize_for_search(text)
    phrases = load_translation_data_raw().get("phrases", [])

    # 1. Exact verified phrase match
    for p in phrases:
        if src_can == "gojri":
            candidates = [
                normalize_for_search(p.get("gojri", "")),
                normalize_for_search(p.get("gojri_roman", "")),
                normalize_for_search(p.get("gojri_devanagari", "")),
            ]
            if norm_query in candidates:
                tgt_text = p.get(tgt_can, "")
                if tgt_text:
                    return TranslationResult(
                        text=tgt_text,
                        status="exact_match",
                        source=src_can,
                        target=tgt_can,
                        confidence=1.0,
                        matched_phrases=[p],
                        notes=f"Verified match from {p.get('id', 'corpus')}",
                    )
        else:
            cand = normalize_for_search(p.get(src_can, ""))
            if norm_query == cand:
                tgt_text = p.get(tgt_can) if tgt_can != "gojri" else p.get("gojri")
                if tgt_text:
                    return TranslationResult(
                        text=tgt_text,
                        status="exact_match",
                        source=src_can,
                        target=tgt_can,
                        confidence=1.0,
                        matched_phrases=[p],
                        notes=f"Verified match from {p.get('id', 'corpus')}",
                    )

    # 2. Single-word lexical lookup fallback
    clean_tokens = text.strip().split()
    if len(clean_tokens) == 1:
        if src_can == "gojri":
            entry = lookup(text)
            if entry:
                field_map = {
                    "english": entry.meaning_en,
                    "hindi": entry.meaning_hi,
                    "urdu": entry.meaning_ur,
                }
                tgt_text = field_map.get(tgt_can)
                if tgt_text:
                    return TranslationResult(
                        text=tgt_text,
                        status="lexical_match",
                        source=src_can,
                        target=tgt_can,
                        confidence=0.85,
                        matched_phrases=[entry.to_dict()],
                        notes=f"Dictionary entry match for '{entry.word}'",
                    )
        else:
            results = search(text, language=src_can, limit=1)
            if results:
                entry = results[0]
                tgt_text = entry.word if tgt_can == "gojri" else getattr(entry, f"meaning_{tgt_can[:2]}", "")
                if tgt_text:
                    return TranslationResult(
                        text=tgt_text,
                        status="lexical_match",
                        source=src_can,
                        target=tgt_can,
                        confidence=0.85,
                        matched_phrases=[entry.to_dict()],
                        notes=f"Dictionary entry match from {src_can}",
                    )

    # 3. Not found in verified datasets
    return TranslationResult(
        text=f"No verified translation available in authenticated corpus for: '{text}'",
        status="not_found",
        source=src_can,
        target=tgt_can,
        confidence=0.0,
        matched_phrases=[],
        notes="Speculative or unverified machine translation is explicitly not produced.",
    )

