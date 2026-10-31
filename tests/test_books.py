"""Tests for Gojri literature, books, and historical corpus subsystem."""

from __future__ import annotations

import pytest

from gojrilang.books import (
    get_book,
    get_page,
    list_books,
    search_books,
)
from gojrilang.exceptions import BookNotFoundError


def test_list_books() -> None:
    books = list_books()
    assert len(books) >= 3
    ids = {b.id for b in books}
    assert "grierson_1908_lsi" in ids
    assert "sharma_1982_narratives" in ids
    assert "losey_2002_writing_gojri" in ids


def test_get_book() -> None:
    book = get_book("grierson_1908_lsi")
    assert book.title.startswith("Linguistic Survey of India")
    assert book.author == "Sir George Abraham Grierson"
    assert book.year == 1908
    assert len(book.pages) == 3


def test_get_missing_book_raises() -> None:
    with pytest.raises(BookNotFoundError):
        get_book("imaginary_ancient_tome")


def test_get_page() -> None:
    page = get_page("grierson_1908_lsi", 1)
    assert page.page_number == 1
    assert "آدمی" in page.text_perso_arabic or "ہک" in page.text_perso_arabic
    assert page.text_devanagari is not None
    assert page.text_roman is not None
    assert "two sons" in page.translation_en.lower()


def test_page_get_text_by_script() -> None:
    page = get_page("sharma_1982_narratives", 1)
    pa = page.get_text("perso-arabic")
    dev = page.get_text("devanagari")
    rom = page.get_text("roman")
    assert "چرواہو" in pa
    assert "चरवाहो" in dev
    assert "charwāho" in rom.lower()


def test_search_books() -> None:
    # Search for known term in Grierson & Sharma texts
    results = search_books("prodigal")
    assert len(results) >= 1
    assert any(r.book_id == "grierson_1908_lsi" for r in results)

    # Search for pastoral term 'flock' or 'ijjaṛ'
    results_flock = search_books("ijjaṛ")
    assert len(results_flock) >= 1
    assert any(r.book_id == "sharma_1982_narratives" for r in results_flock)

