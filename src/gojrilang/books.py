"""Literature and historical corpus subsystem for Gojri language texts.

Provides structured, evidence-based access to verified public domain and
open-access Gojri literature collections (Grierson 1908, Sharma 1982, Losey 2002).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from gojrilang.exceptions import BookNotFoundError
from gojrilang.normalize import normalize_for_search


@dataclass
class BookPage:
    """A single page, poem, or text specimen from a Gojri book."""

    page_number: int
    section_title: str
    text_perso_arabic: str
    text_devanagari: Optional[str]
    text_roman: Optional[str]
    translation_en: str
    notes: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BookPage:
        return cls(
            page_number=int(data["page_number"]),
            section_title=data.get("section_title", ""),
            text_perso_arabic=data.get("text_perso_arabic", ""),
            text_devanagari=data.get("text_devanagari"),
            text_roman=data.get("text_roman"),
            translation_en=data.get("translation_en", ""),
            notes=data.get("notes"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_text(self, script: str = "perso-arabic") -> str:
        """Return the text in the requested script if available."""
        s_clean = script.lower().strip()
        if "perso" in s_clean or "arabic" in s_clean or "urdu" in s_clean:
            return self.text_perso_arabic
        if "devanagari" in s_clean or "hindi" in s_clean:
            return self.text_devanagari or self.text_perso_arabic
        if "roman" in s_clean or "latin" in s_clean:
            return self.text_roman or self.text_perso_arabic
        return self.text_perso_arabic


@dataclass
class BookMetadata:
    """Bibliographic metadata for a Gojri literature collection."""

    id: str
    title: str
    author: str
    year: int
    publisher: str
    dialect: str
    license: str
    description: str
    page_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.id}] '{self.title}' ({self.author}, {self.year}) - {self.page_count} pages"


@dataclass
class BookSearchResult:
    """Result of searching within Gojri literature."""

    book_id: str
    book_title: str
    page_number: int
    section_title: str
    matched_field: str
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.book_id} p.{self.page_number}] {self.section_title} ({self.matched_field}): {self.snippet}"


class Book:
    """A Gojri literary work or language specimen collection."""

    def __init__(self, metadata: BookMetadata, pages: List[BookPage]) -> None:
        self.metadata = metadata
        self.pages = pages
        self._page_map: Dict[int, BookPage] = {p.page_number: p for p in pages}

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def title(self) -> str:
        return self.metadata.title

    @property
    def author(self) -> str:
        return self.metadata.author

    @property
    def year(self) -> int:
        return self.metadata.year

    @property
    def dialect(self) -> str:
        return self.metadata.dialect

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Book:
        raw_pages = data.get("pages", [])
        pages = [BookPage.from_dict(p) for p in raw_pages]
        meta = BookMetadata(
            id=data["id"],
            title=data["title"],
            author=data.get("author", "Unknown"),
            year=int(data.get("year", 0)),
            publisher=data.get("publisher", ""),
            dialect=data.get("dialect", "General Gojri"),
            license=data.get("license", "Public Domain"),
            description=data.get("description", ""),
            page_count=len(pages),
        )
        return cls(metadata=meta, pages=pages)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.metadata.to_dict(),
            "pages": [p.to_dict() for p in self.pages],
        }

    def get_page(self, page_number: int) -> BookPage:
        """Retrieve a specific page by page number."""
        page = self._page_map.get(page_number)
        if not page:
            raise BookNotFoundError(f"{self.id} (page {page_number})")
        return page

    def iter_pages(self) -> Iterator[BookPage]:
        """Iterate over all pages."""
        return iter(self.pages)

    def search(self, query: str, case_sensitive: bool = False) -> List[BookSearchResult]:
        """Search across all text fields of this book."""
        if not query or not query.strip():
            return []

        q = query.strip() if case_sensitive else query.strip().lower()
        q_norm = normalize_for_search(query)
        results: List[BookSearchResult] = []

        for p in self.pages:
            fields = [
                ("text_perso_arabic", p.text_perso_arabic),
                ("text_devanagari", p.text_devanagari or ""),
                ("text_roman", p.text_roman or ""),
                ("translation_en", p.translation_en),
                ("section_title", p.section_title),
                ("notes", p.notes or ""),
            ]
            for fname, val in fields:
                target = val if case_sensitive else val.lower()
                target_norm = normalize_for_search(val)
                if q in target or (q_norm and q_norm in target_norm):
                    idx = target.find(q)
                    if idx == -1 and q_norm:
                        idx = target_norm.find(q_norm)
                    if idx == -1:
                        idx = 0
                    start = max(0, idx - 30)
                    end = min(len(val), idx + len(query) + 30)
                    snippet = ("..." if start > 0 else "") + val[start:end].strip() + ("..." if end < len(val) else "")
                    results.append(
                        BookSearchResult(
                            book_id=self.metadata.id,
                            book_title=self.metadata.title,
                            page_number=p.page_number,
                            section_title=p.section_title,
                            matched_field=fname,
                            snippet=snippet,
                        )
                    )
                    break
        return results

    def __repr__(self) -> str:
        return f"<Book id='{self.id}' title='{self.title}' pages={len(self.pages)}>"


_BOOKS_REGISTRY: Optional[Dict[str, Book]] = None


def _get_registry() -> Dict[str, Book]:
    global _BOOKS_REGISTRY
    if _BOOKS_REGISTRY is None:
        ref = resources.files("gojrilang.data").joinpath("books.json")
        with ref.open("r", encoding="utf-8") as f:
            data = json.load(f)
        _BOOKS_REGISTRY = {
            b["id"]: Book.from_dict(b) for b in data.get("books", [])
        }
    return _BOOKS_REGISTRY


def list_books(category: Optional[str] = None) -> List[BookMetadata]:
    """List metadata for all documented Gojri literature collections.

    Args:
        category: Optional search term or category filter across id, title, dialect, or description.
    """
    books = [b.metadata for b in _get_registry().values()]
    if category:
        cat_clean = category.strip().lower()
        books = [
            b for b in books
            if cat_clean in b.title.lower()
            or cat_clean in b.dialect.lower()
            or cat_clean in b.description.lower()
            or cat_clean in b.id.lower()
        ]
    return books


def register_book(book: Union[Book, Dict[str, Any]]) -> Book:
    """Register a new or custom Gojri literature book in the active registry.

    Args:
        book: A Book instance or a dictionary conforming to the book schema.

    Returns:
        The registered Book instance.
    """
    if isinstance(book, dict):
        book_obj = Book.from_dict(book)
    elif isinstance(book, Book):
        book_obj = book
    else:
        raise TypeError(f"Expected Book or dict, got {type(book).__name__}")

    reg = _get_registry()
    reg[book_obj.id] = book_obj
    return book_obj


def import_book_file(filepath: Union[str, Path]) -> Book:
    """Load and register a Gojri literature book from a JSON file.

    Args:
        filepath: Path to the JSON book file.

    Returns:
        The loaded and registered Book instance.
    """
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"Book file '{p}' does not exist.")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return register_book(data)


def reset_registry() -> None:
    """Reset the cached book registry so it reloads from packaged data on next access."""
    global _BOOKS_REGISTRY
    _BOOKS_REGISTRY = None


def get_book(book_id: str) -> Book:
    """Retrieve a Gojri literature book by its identifier."""
    reg = _get_registry()
    book = reg.get(book_id.strip())
    if not book:
        for k, v in reg.items():
            if k.lower() == book_id.strip().lower():
                return v
        raise BookNotFoundError(book_id)
    return book


def get_page(book_id: str, page_number: int) -> BookPage:
    """Retrieve a specific page from a Gojri book."""
    return get_book(book_id).get_page(page_number)


def search_books(query: str, case_sensitive: bool = False) -> List[BookSearchResult]:
    """Search for words, phrases, or topics across all documented Gojri texts."""
    all_results: List[BookSearchResult] = []
    for b in _get_registry().values():
        all_results.extend(b.search(query, case_sensitive=case_sensitive))
    return all_results

