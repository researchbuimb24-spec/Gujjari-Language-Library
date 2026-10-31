"""Tests for scalable indexed SQLite storage and batch ingestion."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from gojrilang.storage import GojriLexiconDB


def test_db_init_and_build_from_bundled() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_lexicon.db"
        db = GojriLexiconDB(db_path)
        assert db.count() == 0

        count = db.build_from_bundled_data()
        assert count >= 60
        assert db.count() == count


def test_db_lookup_and_search() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_lexicon.db"
        db = GojriLexiconDB(db_path)
        db.build_from_bundled_data()

        # Lookup
        entry = db.lookup("گھوڑو")
        assert entry is not None
        assert entry.meaning_en == "horse"

        # Search by English
        results = db.search("water", language="english")
        assert len(results) >= 1
        assert any(r.word == "پاݨی" for r in results)


def test_db_import_csv() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_lexicon.db"
        csv_path = Path(tmpdir) / "sample_import.csv"

        csv_content = """word,meaning_en,meaning_hi,meaning_ur,pos,word_roman,word_devanagari,dialect,source,verification_status
مٹھائی,sweets,मिठाई,مٹھائی,noun,miṭhāī,मिठाई,general,Fieldwork,community_reviewed
کتاب,book,किताब,کتاب,noun,kitāb,किताब,general,Fieldwork,community_reviewed
"""
        csv_path.write_text(csv_content, encoding="utf-8")

        db = GojriLexiconDB(db_path)
        imported = db.import_from_csv(csv_path)
        assert imported == 2
        assert db.count() == 2

        entry = db.lookup("مٹھائی")
        assert entry is not None
        assert entry.meaning_en == "sweets"
        assert entry.verification_status == "community_reviewed"

