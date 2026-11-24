"""Tests for Gojri epics subsystem (Ramayana, Mahabharata, and related epic lore)."""

import pytest
from gojrilang.epics import (
    Epic,
    EpicChapter,
    EpicKandaParva,
    EpicVerse,
    get_epic,
    get_epic_chapter,
    get_epic_verse,
    list_epics,
    register_epic,
    search_epics,
)
from gojrilang.exceptions import GojriLangError


def test_list_epics():
    epics = list_epics()
    assert len(epics) >= 2
    epic_ids = {e["id"] for e in epics}
    assert "gojri_ramayana" in epic_ids
    assert "gojri_mahabharata" in epic_ids


def test_get_epic_ramayana():
    epic = get_epic("gojri_ramayana")
    assert isinstance(epic, Epic)
    assert epic.id == "gojri_ramayana"
    assert "Ramayana" in epic.title
    assert "Oral" in epic.tradition or "Ballad" in epic.tradition or "katha" in epic.tradition.lower()
    assert len(epic.sections) >= 2

    # Check Bal Kanda
    bal_kanda = epic.sections[0]
    assert "Bal Kanda" in bal_kanda.title
    assert len(bal_kanda.chapters) >= 1
    assert len(bal_kanda.chapters[0].verses) >= 1

    v1 = bal_kanda.chapters[0].verses[0]
    assert v1.verse_num == 1
    assert "جنک" in v1.text_perso_arabic or "سیتا" in v1.text_perso_arabic or "Janak" in v1.translation_en or "Sita" in v1.translation_en
    assert v1.text_roman is not None
    assert v1.text_devanagari is not None
    assert len(v1.vocabulary) >= 1


def test_get_epic_mahabharata():
    epic = get_epic("gojri_mahabharata")
    assert isinstance(epic, Epic)
    assert epic.id == "gojri_mahabharata"
    assert "Mahabharata" in epic.title

    section_titles = [s.title for s in epic.sections]
    assert any("Bhishma Parva" in t or "Kurukshetra" in t for t in section_titles)
    assert any("Virata Parva" in t or "Pastoral" in t for t in section_titles)

    # Check Bhagavad Gita verse in Bhishma Parva
    bhishma = next(s for s in epic.sections if "Bhishma" in s.title)
    gita_chap = bhishma.chapters[0]
    assert len(gita_chap.verses) >= 1
    v = gita_chap.verses[0]
    assert v.text_roman is not None
    assert "کرم" in v.text_perso_arabic or "karam" in (v.text_roman or "").lower()
    assert "duty" in v.translation_en.lower()


def test_get_epic_chapter():
    chap = get_epic_chapter("gojri_ramayana", 1)
    assert isinstance(chap, EpicChapter)
    assert chap.chapter_num == 1
    assert len(chap.verses) >= 1


def test_get_epic_verse():
    verse = get_epic_verse("gojri_ramayana", 1, 1)
    assert isinstance(verse, EpicVerse)
    assert verse.verse_num == 1
    assert verse.text_perso_arabic is not None
    assert verse.translation_en is not None

    # Test with section explicitly passed
    verse_sec = get_epic_verse("gojri_ramayana", "bal_kanda", 1, 1)
    assert isinstance(verse_sec, EpicVerse)
    assert verse_sec.verse_num == 1


def test_get_missing_epic_raises():
    with pytest.raises(GojriLangError):
        get_epic("nonexistent_epic_123")


def test_search_epics():
    results = search_epics("duty")
    assert len(results) >= 1
    assert any(r["epic_id"] == "gojri_mahabharata" for r in results)

    results_ar = search_epics("سیتا")
    assert len(results_ar) >= 1
    assert any(r["epic_id"] == "gojri_ramayana" for r in results_ar)


def test_dynamic_register_epic():
    new_epic = Epic(
        id="test_epic",
        title="Test Epic Lore",
        title_gojri="ٹیسٹ کتھا",
        tradition="test_tradition",
        source="Field Recordings",
        sections=[
            EpicKandaParva(
                id="sec_1",
                section_num=1,
                title="Section 1",
                chapters=[
                    EpicChapter(
                        chapter_num=1,
                        title="Chapter 1",
                        verses=[
                            EpicVerse(
                                verse_num=1,
                                text_perso_arabic="ٹیسٹ متن",
                                translation_en="Test text",
                            )
                        ]
                    )
                ]
            )
        ]
    )
    register_epic(new_epic)
    retrieved = get_epic("test_epic")
    assert retrieved.title == "Test Epic Lore"
    assert len(retrieved.sections) == 1
