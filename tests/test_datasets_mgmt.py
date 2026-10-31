"""Tests for GojriLang dataset management, validation, import, and export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gojrilang.datasets import (
    ImportReport,
    ValidationReport,
    export_file,
    get_dataset_stats,
    import_file,
    validate,
)
from gojrilang.exceptions import DatasetValidationError


def test_dataset_stats_comprehensive() -> None:
    stats = get_dataset_stats()
    assert "dictionary" in stats
    assert "grammar" in stats
    assert "culture" in stats
    assert "translation" in stats
    assert "dialects" in stats
    assert "books" in stats
    assert stats["dialects"]["total_profiles"] >= 4
    assert stats["books"]["total_books"] >= 3


def test_validate_valid_dataset(tmp_path: Path) -> None:
    valid_data = {
        "entries": [
            {
                "id": "test_001",
                "word": "گھوڑو",
                "pos": "noun",
                "meaning_en": "horse",
                "meaning_hi": "घोड़ा",
                "meaning_ur": "گھوڑا",
                "script": "perso-arabic",
                "source": "SHARMA_1982",
                "verification_status": "verified",
            }
        ]
    }
    file_path = tmp_path / "valid_dict.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(valid_data, f)

    report = validate(file_path, dataset_type="dictionary")
    assert isinstance(report, ValidationReport)
    assert report.is_valid is True
    assert report.total_records == 1
    assert len(report.errors) == 0


def test_validate_invalid_dataset_missing_fields(tmp_path: Path) -> None:
    invalid_data = {
        "entries": [
            {
                "id": "bad_001",
                "word": "گھوڑو",
                # Missing pos, meaning_en, etc.
            }
        ]
    }
    file_path = tmp_path / "bad_dict.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(invalid_data, f)

    report = validate(file_path, dataset_type="dictionary")
    assert report.is_valid is False
    assert len(report.errors) > 0


def test_export_and_import_json(tmp_path: Path) -> None:
    export_path = tmp_path / "exported_dict.json"
    exported = export_file(export_path, dataset_name="dictionary", fmt="json")
    assert exported.is_file()

    # Now import with conflict_resolution='skip'
    report = import_file(exported, target_dataset="dictionary", conflict_resolution="skip")
    assert isinstance(report, ImportReport)
    # Since all IDs in exported already exist in bundled dictionary, skipped_count should equal total
    assert report.skipped_count > 0
    assert report.imported_count == 0


def test_export_csv_and_jsonl(tmp_path: Path) -> None:
    csv_path = tmp_path / "exported_culture.csv"
    exported_csv = export_file(csv_path, dataset_name="culture", fmt="csv")
    assert exported_csv.is_file()

    jsonl_path = tmp_path / "exported_grammar.jsonl"
    exported_jsonl = export_file(jsonl_path, dataset_name="grammar", fmt="jsonl")
    assert exported_jsonl.is_file()


def test_import_conflict_resolution_fail(tmp_path: Path) -> None:
    # Export dictionary and try to import with conflict_resolution='fail'
    export_path = tmp_path / "conflict_dict.json"
    export_file(export_path, dataset_name="dictionary", fmt="json")

    with pytest.raises(DatasetValidationError):
        import_file(export_path, target_dataset="dictionary", conflict_resolution="fail")

