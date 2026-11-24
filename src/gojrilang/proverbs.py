"""Dedicated proverbs (Akhan / Zarb-ul-Masal) subsystem for Gojri."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from gojrilang.culture import CulturalItem, list_proverbs as _list_proverbs, search_culture


def list_proverbs(dialect: Optional[str] = None) -> List[CulturalItem]:
    """Return all verified Gojri proverbs, optionally filtered by dialect."""
    return _list_proverbs(dialect=dialect)


def get_proverb(proverb_id: str) -> Optional[CulturalItem]:
    """Retrieve a proverb by its identifier (e.g. 'CULT_PROV_01')."""
    from gojrilang.culture import get_cultural_item
    item = get_cultural_item(proverb_id)
    if item and item.category == "proverbs":
        return item
    return None


def search_proverbs(query: str, limit: Optional[int] = None) -> List[CulturalItem]:
    """Search within verified Gojri proverbs."""
    return search_culture(query, category="proverbs", limit=limit)
