"""Tests for Gojri literature, books, and historical corpus subsystem."""

from __future__ import annotations

import pytest

from gojrilang.books import (
    Book,
    BookMetadata,
    BookPage,
    get_book,
    get_page,
    import_book_file,
    list_books,
    register_book,
    reset_registry,
    search_books,
)
from gojrilang.exceptions import BookNotFoundError


def test_list_books() -> None:
    reset_registry()
    books = list_books()
    assert len(books) == 10
    ids = {b.id for b in books}
    assert "grierson_1908_lsi" in ids
    assert "sharma_1982_narratives" in ids
    assert "losey_2002_writing_gojri" in ids
    assert "gojri_ramkatha_oral" in ids
    assert "gojri_pandav_katha_oral" in ids
    assert "gojri_lok_geet_jkaacl" in ids
    assert "kalam_e_nizam_larvi" in ids
    assert "sohni_mahiwal_gojri" in ids
    assert "saiful_malook_gojri" in ids
    assert "baranmah_pir_panjal" in ids


def test_ramkatha_epic_book() -> None:
    book = get_book("gojri_ramkatha_oral")
    assert "Ramayana" in book.title or "Ramkatha" in book.title
    assert len(book.pages) == 3
    p1 = book.get_page(1)
    assert "رام چندر" in p1.text_perso_arabic
    assert "राम चन्द्र" in (p1.text_devanagari or "")
    assert "exile" in p1.translation_en.lower()

    # Search within Ramkatha
    results = book.search("Jatayu")
    assert len(results) >= 1
    assert results[0].page_number == 2


def test_pandav_katha_epic_book() -> None:
    book = get_book("gojri_pandav_katha_oral")
    assert "Mahabharata" in book.title or "Pandav" in book.title
    assert len(book.pages) == 3
    p2 = book.get_page(2)
    assert "کروکھشیتر" in p2.text_perso_arabic or "ارحن" in p2.text_perso_arabic or "شری کرشن" in p2.text_perso_arabic
    assert "duty" in p2.translation_en.lower() or "fruits" in p2.translation_en.lower()


def test_gojri_lok_geet_and_songbook() -> None:
    book = get_book("gojri_lok_geet_jkaacl")
    assert "Lok Geet" in book.title or "Folk Songs" in book.title
    assert len(book.pages) == 3
    # Check page 1 has Chhaint
    assert "Chhaint" in book.get_page(1).section_title
    # Check page 3 has caravan migration
    assert "Tāṇḍo" in book.get_page(3).section_title or "Migration" in book.get_page(3).section_title


def test_sufi_and_pastoral_tales() -> None:
    sohni = get_book("sohni_mahiwal_gojri")
    assert "Sohni" in sohni.title
    assert "Mahiwal" in sohni.title

    larvi = get_book("kalam_e_nizam_larvi")
    assert "Nizam" in larvi.title

    saif = get_book("saiful_malook_gojri")
    assert "Saiful Malook" in saif.title

    bm = get_book("baranmah_pir_panjal")
    assert "Baranmah" in bm.title


def test_dynamic_register_book() -> None:
    custom_book = {
        "id": "test_custom_manuscript",
        "title": "Custom Gojri Manuscript",
        "author": "Community Scribe",
        "year": 2026,
        "publisher": "Pir Panjal Heritage Press",
        "dialect": "Poonchi Gojri",
        "license": "CC-BY-4.0",
        "description": "A newly recorded oral ballad.",
        "pages": [
            {
                "page_number": 1,
                "section_title": "Invocation",
                "text_perso_arabic": "رب سچے رو نام لے کے شروعات کیتی۔",
                "text_devanagari": "रब सच्चे रो नाम ले के शुरुआत कीती।",
                "text_roman": "Rab sache ro nām le ke shuru'āt kītī.",
                "translation_en": "Beginning with the name of the True Lord.",
                "notes": "Introductory pastoral invocation."
            }
        ]
    }
    b = register_book(custom_book)
    assert b.id == "test_custom_manuscript"
    retrieved = get_book("test_custom_manuscript")
    assert retrieved.title == "Custom Gojri Manuscript"

    # Reset registry to restore packaged state
    reset_registry()
    assert len(list_books()) == 10


def test_list_books_category_filter() -> None:
    epic_books = list_books(category="epic")
    assert len(epic_books) >= 2
    ids = {b.id for b in epic_books}
    assert "gojri_ramkatha_oral" in ids or "gojri_pandav_katha_oral" in ids or "sohni_mahiwal_gojri" in ids


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

