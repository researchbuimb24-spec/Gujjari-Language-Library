"""Universal multi-domain search across Gojri digital language infrastructure.

Allows simultaneous cross-domain querying across:
1. Dictionary headwords & glosses
2. Literature books
3. Classical epics (Ramayana & Mahabharata)
4. Traditional songs & lyrics
5. Folk stories & dastans
6. Poetry & couplets
7. Cultural proverbs & pastoral terms
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from gojrilang.books import search_books
from gojrilang.culture import search_culture
from gojrilang.dictionary import search as search_dictionary
from gojrilang.epics import search_epics
from gojrilang.folk_stories import search_stories
from gojrilang.poetry import search_poetry
from gojrilang.songs import search_songs


def universal_search(
    query: str,
    domains: Optional[List[str]] = None,
    limit_per_domain: int = 5,
) -> Dict[str, Any]:
    """Perform a unified query across all Gojri digital language subsystems.

    Args:
        query: Search term or phrase in any script (Gojri, English, Hindi, Urdu).
        domains: Optional subset of domains ('dictionary', 'books', 'epics', 'songs', 'poetry', 'stories', 'culture').
        limit_per_domain: Max results returned per individual domain.

    Returns:
        Aggregated dictionary containing matched records grouped by subsystem.
    """
    if not query or not query.strip():
        return {"query": query, "total_matches": 0, "results": {}}

    selected = {d.strip().lower() for d in domains} if domains else {
        "dictionary", "books", "epics", "songs", "poetry", "stories", "culture"
    }

    results: Dict[str, List[Any]] = {}
    total = 0

    if "dictionary" in selected:
        dict_res = search_dictionary(query, limit=limit_per_domain)
        results["dictionary"] = [e.to_dict() for e in dict_res]
        total += len(dict_res)

    if "books" in selected:
        book_res = search_books(query)[:limit_per_domain]
        results["books"] = [b.to_dict() for b in book_res]
        total += len(book_res)

    if "epics" in selected:
        epic_res = search_epics(query)[:limit_per_domain]
        results["epics"] = epic_res
        total += len(epic_res)

    if "songs" in selected:
        song_res = search_songs(query)[:limit_per_domain]
        results["songs"] = [s.to_dict() for s in song_res]
        total += len(song_res)

    if "poetry" in selected:
        poem_res = search_poetry(query)[:limit_per_domain]
        results["poetry"] = poem_res
        total += len(poem_res)

    if "stories" in selected:
        story_res = search_stories(query)[:limit_per_domain]
        results["stories"] = story_res
        total += len(story_res)

    if "culture" in selected:
        cult_res = search_culture(query, limit=limit_per_domain)
        results["culture"] = [c.to_dict() for c in cult_res]
        total += len(cult_res)

    return {
        "query": query,
        "total_matches": total,
        "results": results,
    }
