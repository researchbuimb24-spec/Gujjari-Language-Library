"""Cultural and oral heritage module for Gojri language preservation.

Includes authentic proverbs (Akhan), pastoral terminology, and folk traditions
documented in research works by Dr. Javaid Rahi and JKAACL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.datasets import load_cultural_data_raw
from gojrilang.normalize import normalize_for_search


@dataclass
class CulturalItem:
    """An authenticated cultural entry, proverb, or traditional term."""

    id: str
    category: str
    title: str
    text: str
    translation_en: str
    translation_hi: str
    translation_ur: str
    explanation: str
    region: str
    source: str
    verification_status: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CulturalItem:
        return cls(
            id=data["id"],
            category=data["category"],
            title=data.get("title", ""),
            text=data["text"],
            translation_en=data.get("translation_en", ""),
            translation_hi=data.get("translation_hi", ""),
            translation_ur=data.get("translation_ur", ""),
            explanation=data.get("explanation", ""),
            region=data.get("region", "General Gojri"),
            source=data.get("source", "Unspecified"),
            verification_status=data.get("verification_status", "provisional"),
            text_devanagari=data.get("text_devanagari"),
            text_roman=data.get("text_roman"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        roman_part = f" ({self.text_roman})" if self.text_roman else ""
        return (
            f"[{self.id}] [{self.category.upper()}] {self.text}{roman_part}: "
            f"'{self.translation_en}' [{self.verification_status}]"
        )


def _load_all_items() -> List[CulturalItem]:
    raw = load_cultural_data_raw()
    return [CulturalItem.from_dict(item) for item in raw.get("items", [])]


def list_proverbs(dialect: Optional[str] = None) -> List[CulturalItem]:
    """Return all verified Gojri proverbs (Akhan / Zarb-ul-Masal).

    Args:
        dialect: Optional regional filter.

    Returns:
        List of CulturalItem objects representing proverbs.
    """
    items = _load_all_items()
    proverbs = [i for i in items if i.category == "proverbs"]
    if dialect:
        dia_clean = dialect.strip().lower()
        proverbs = [
            p for p in proverbs
            if dia_clean in p.region.lower() or "general" in p.region.lower()
        ]
    return proverbs


def list_songs(dialect: Optional[str] = None) -> List[CulturalItem]:
    """Return all verified Gojri traditional songs (Chhaint, Mahya, Singran Ka Geet, Bait, Lori, Dholak).

    Args:
        dialect: Optional regional filter.

    Returns:
        List of CulturalItem objects representing traditional songs.
    """
    items = _load_all_items()
    songs = [i for i in items if i.category == "songs"]
    if dialect:
        dia_clean = dialect.strip().lower()
        songs = [
            s for s in songs
            if dia_clean in s.region.lower() or "general" in s.region.lower()
        ]
    return songs


def list_items(category: Optional[str] = None) -> List[CulturalItem]:
    """Return all cultural items, optionally filtered by category.

    Args:
        category: Optional category filter (e.g. 'proverbs', 'pastoral_terms', 'folklore', 'songs').

    Returns:
        List of CulturalItem objects.
    """
    items = _load_all_items()
    if category:
        cat_clean = category.strip().lower()
        items = [i for i in items if i.category.lower() == cat_clean]
    return items


def list_cultural_categories() -> List[str]:
    """Return all categories present in the cultural heritage dataset."""
    items = _load_all_items()
    return sorted(list({i.category for i in items}))


def get_cultural_item(item_id: str) -> Optional[CulturalItem]:
    """Retrieve a specific cultural entry by ID."""
    clean_id = item_id.strip().lower()
    for item in _load_all_items():
        if item.id.lower() == clean_id:
            return item
    return None


def search_culture(
    query: str,
    category: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[CulturalItem]:
    """Search Gojri proverbs, idioms, and pastoral terminology.

    Matches query against Gojri text, Roman transcription, translations,
    and cultural explanations.

    Args:
        query: Search keyword or phrase.
        category: Optional category filter (e.g. 'proverbs', 'pastoral_terms').
        limit: Maximum number of records to return.

    Returns:
        List of matching CulturalItem records.
    """
    if not query or not query.strip():
        return []

    items = _load_all_items()
    q_norm = normalize_for_search(query)
    results: List[CulturalItem] = []

    for item in items:
        if category and item.category.lower() != category.strip().lower():
            continue

        searchable_corpus = [
            normalize_for_search(item.text),
            normalize_for_search(item.text_devanagari or ""),
            normalize_for_search(item.text_roman or ""),
            normalize_for_search(item.title),
            normalize_for_search(item.translation_en),
            normalize_for_search(item.translation_hi),
            normalize_for_search(item.translation_ur),
            normalize_for_search(item.explanation),
        ]

        if any(q_norm in field for field in searchable_corpus if field):
            results.append(item)
            if limit is not None and len(results) >= limit:
                break

    return results

