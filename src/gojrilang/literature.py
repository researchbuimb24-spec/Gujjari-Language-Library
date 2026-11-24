"""Unified digital literature archive for Gojri language texts.

Unifies published books, classical epics (Ramayana, Mahabharata), poetry collections
(Bait, Ghazal, Dohra, Nazm), and traditional oral folktales (Dastan, Lok Kahani).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.books import (
    Book,
    BookMetadata,
    BookPage,
    BookSearchResult,
    get_book,
    get_page,
    import_book_file,
    list_books,
    register_book,
    search_books,
)
from gojrilang.epics import (
    Epic,
    EpicChapter,
    EpicVerse,
    get_epic,
    get_epic_chapter,
    get_epic_verse,
    list_epics,
    search_epics,
)
from gojrilang.folk_stories import (
    FolkStory,
    get_story,
    list_stories,
    search_stories,
)
from gojrilang.poetry import (
    Poem,
    get_poem,
    list_poetic_forms,
    list_poems,
    search_poetry,
)


@dataclass
class LiteratureOverview:
    """Summary of all documented literature collections across categories."""

    total_books: int
    total_epics: int
    total_poems: int
    total_stories: int
    book_titles: List[str]
    epic_titles: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_literature_overview() -> LiteratureOverview:
    """Return an overview of all documented Gojri literature collections."""
    books = list_books()
    epics = list_epics()
    poems = list_poems()
    stories = list_stories()
    return LiteratureOverview(
        total_books=len(books),
        total_epics=len(epics),
        total_poems=len(poems),
        total_stories=len(stories),
        book_titles=[b.title for b in books],
        epic_titles=[e["title"] for e in epics],
    )


def search_all_literature(query: str) -> Dict[str, List[Any]]:
    """Search across books, epics, poetry, and folktales simultaneously."""
    book_matches = [b.to_dict() for b in search_books(query)]
    epic_matches = search_epics(query)
    poem_matches = search_poetry(query)
    story_matches = search_stories(query)
    return {
        "query": query,
        "books": book_matches,
        "epics": epic_matches,
        "poetry": poem_matches,
        "folk_stories": story_matches,
        "total_matches": len(book_matches) + len(epic_matches) + len(poem_matches) + len(story_matches),
    }
