"""Dataset loading, caching, schema validation, and management for GojriLang.

All bundled data files are verified linguistic records from published scholarly sources
(CIIL, JKAACL, SIL).
"""

from __future__ import annotations

import csv
import functools
import json
from dataclasses import asdict, dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from gojrilang.exceptions import DataSchemaValidationError, DatasetValidationError


REQUIRED_DICTIONARY_FIELDS: Set[str] = {
    "id",
    "word",
    "pos",
    "meaning_en",
    "meaning_hi",
    "meaning_ur",
    "script",
    "source",
    "verification_status",
}

VALID_VERIFICATION_STATUSES: Set[str] = {
    "verified",
    "community_reviewed",
    "provisional",
    "experimental",
    "attested_pattern",
}


@dataclass
class ValidationReport:
    """Detailed validation results for a dataset file."""

    is_valid: bool
    total_records: int
    errors: List[str]
    warnings: List[str]
    dataset_type: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return (
            f"ValidationReport({status}, type={self.dataset_type}, records={self.total_records}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


@dataclass
class ImportReport:
    """Report summarizing dataset import operations."""

    imported_count: int
    skipped_count: int
    overwritten_count: int
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return (
            f"ImportReport(imported={self.imported_count}, skipped={self.skipped_count}, "
            f"overwritten={self.overwritten_count}, errors={len(self.errors)})"
        )


def _validate_dictionary_data(data: Dict[str, Any]) -> None:
    """Validate loaded dictionary data structure."""
    errors: List[str] = []
    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append("Top-level 'entries' key must be a list.")
        raise DataSchemaValidationError("dictionary.json", errors)

    for idx, entry in enumerate(entries):
        missing = REQUIRED_DICTIONARY_FIELDS - entry.keys()
        if missing:
            errors.append(f"Entry #{idx} (id={entry.get('id', 'N/A')}) missing required fields: {missing}")
        status = entry.get("verification_status")
        if status not in VALID_VERIFICATION_STATUSES:
            errors.append(
                f"Entry #{idx} has invalid verification_status '{status}'. "
                f"Must be one of {VALID_VERIFICATION_STATUSES}"
            )

    if errors:
        raise DataSchemaValidationError("dictionary.json", errors)


@functools.lru_cache(maxsize=1)
def load_dictionary_raw() -> Dict[str, Any]:
    """Load raw dictionary JSON data with schema validation."""
    ref = resources.files("gojrilang.data").joinpath("dictionary.json")
    with ref.open("r", encoding="utf-8") as f:
        data = json.load(f)
    _validate_dictionary_data(data)
    return data


@functools.lru_cache(maxsize=1)
def load_dictionary_entries() -> List[Dict[str, Any]]:
    """Return all dictionary entries."""
    return load_dictionary_raw().get("entries", [])


@functools.lru_cache(maxsize=1)
def load_grammar_rules_raw() -> Dict[str, Any]:
    """Load grammar rules JSON."""
    ref = resources.files("gojrilang.data").joinpath("grammar_rules.json")
    with ref.open("r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=1)
def load_cultural_data_raw() -> Dict[str, Any]:
    """Load cultural and oral heritage JSON."""
    ref = resources.files("gojrilang.data").joinpath("culture.json")
    with ref.open("r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=1)
def load_translation_data_raw() -> Dict[str, Any]:
    """Load verified translation phrases."""
    ref = resources.files("gojrilang.data").joinpath("translation_phrases.json")
    with ref.open("r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=1)
def load_dialects_raw() -> Dict[str, Any]:
    """Load dialect profiles JSON."""
    ref = resources.files("gojrilang.data").joinpath("dialects.json")
    with ref.open("r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=1)
def load_books_raw() -> Dict[str, Any]:
    """Load verified literature books JSON."""
    ref = resources.files("gojrilang.data").joinpath("books.json")
    with ref.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_dataset_stats() -> Dict[str, Any]:
    """Return an evidence-based summary of all bundled datasets."""
    dict_data = load_dictionary_raw()
    grammar_data = load_grammar_rules_raw()
    culture_data = load_cultural_data_raw()
    trans_data = load_translation_data_raw()
    dialects_data = load_dialects_raw()
    books_data = load_books_raw()

    dict_entries = dict_data.get("entries", [])
    rules = grammar_data.get("rules", [])
    cult_items = culture_data.get("items", [])
    trans_items = trans_data.get("phrases", [])
    profiles = dialects_data.get("profiles", [])
    books = books_data.get("books", [])

    total_pages = sum(len(b.get("pages", [])) for b in books)

    return {
        "language": "Gujari / Gojri (ISO 639-3: gju)",
        "dictionary": {
            "total_entries": len(dict_entries),
            "verified_count": sum(
                1 for e in dict_entries if e.get("verification_status") == "verified"
            ),
            "parts_of_speech": sorted(
                list({e.get("pos") for e in dict_entries if e.get("pos")})
            ),
        },
        "grammar": {
            "total_rules": len(rules),
            "categories": sorted(
                list({r.get("category") for r in rules if r.get("category")})
            ),
        },
        "culture": {
            "total_items": len(cult_items),
            "categories": sorted(
                list({c.get("category") for c in cult_items if c.get("category")})
            ),
        },
        "translation": {
            "total_phrases": len(trans_items),
            "supported_languages": ["gojri", "english", "hindi", "urdu"],
        },
        "dialects": {
            "total_profiles": len(profiles),
            "profile_ids": [p.get("id") for p in profiles],
        },
        "books": {
            "total_books": len(books),
            "total_pages": total_pages,
            "book_ids": [b.get("id") for b in books],
        },
    }


def _read_records_from_file(path: Path) -> List[Dict[str, Any]]:
    """Parse records from JSON, JSONL, or CSV file."""
    suffix = path.suffix.lower()
    records: List[Dict[str, Any]] = []

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, list):
                records = content
            elif isinstance(content, dict):
                # Check for standard wrapper keys
                for k in ("entries", "phrases", "rules", "items", "books", "profiles", "dictionary", "grammar", "culture", "translation", "dialects"):
                    if k in content and isinstance(content[k], list):
                        records = content[k]
                        break
                if not records:
                    records = [content]
    elif suffix == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                clean = line.strip()
                if clean:
                    try:
                        records.append(json.loads(clean))
                    except json.JSONDecodeError as err:
                        raise DatasetValidationError(f"Invalid JSON on line {line_no}: {err}")
    elif suffix == ".csv":
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
    else:
        raise DatasetValidationError(f"Unsupported file extension '{suffix}'. Use .json, .jsonl, or .csv.")

    return records


def validate(
    filepath: Union[str, Path],
    dataset_type: str = "dictionary",
) -> ValidationReport:
    """Validate a candidate dataset file against GojriLang schemas.

    Args:
        filepath: Path to the dataset file (.json, .jsonl, .csv).
        dataset_type: Expected dataset type ('dictionary', 'grammar', 'culture', 'phrases').

    Returns:
        ValidationReport dataclass containing validation status and diagnostics.
    """
    path = Path(filepath)
    if not path.is_file():
        return ValidationReport(
            is_valid=False,
            total_records=0,
            errors=[f"File '{path}' does not exist."],
            warnings=[],
            dataset_type=dataset_type,
        )

    errors: List[str] = []
    warnings: List[str] = []

    try:
        records = _read_records_from_file(path)
    except Exception as e:
        return ValidationReport(
            is_valid=False,
            total_records=0,
            errors=[f"Failed to read file: {e}"],
            warnings=[],
            dataset_type=dataset_type,
        )

    if not records:
        errors.append("Dataset file contains 0 records.")
        return ValidationReport(
            is_valid=False,
            total_records=0,
            errors=errors,
            warnings=warnings,
            dataset_type=dataset_type,
        )

    seen_ids: Set[str] = set()

    if dataset_type == "dictionary":
        for idx, rec in enumerate(records):
            rec_id = rec.get("id")
            if not rec_id:
                errors.append(f"Record #{idx} is missing 'id'.")
            elif rec_id in seen_ids:
                errors.append(f"Duplicate entry id '{rec_id}' at record #{idx}.")
            else:
                seen_ids.add(rec_id)

            missing = REQUIRED_DICTIONARY_FIELDS - rec.keys()
            if missing:
                errors.append(f"Record #{idx} (id={rec_id or 'unknown'}) is missing fields: {missing}")

            v_status = rec.get("verification_status")
            if v_status and v_status not in VALID_VERIFICATION_STATUSES:
                errors.append(
                    f"Record #{idx} has invalid verification_status '{v_status}'. Allowed: {VALID_VERIFICATION_STATUSES}"
                )

            if not rec.get("word"):
                errors.append(f"Record #{idx} has empty 'word'.")
            if not rec.get("meaning_en") and not rec.get("meaning_ur") and not rec.get("meaning_hi"):
                warnings.append(f"Record #{idx} (id={rec_id}) has no English, Urdu, or Hindi meaning.")

    return ValidationReport(
        is_valid=len(errors) == 0,
        total_records=len(records),
        errors=errors,
        warnings=warnings,
        dataset_type=dataset_type,
    )


def import_file(
    filepath: Union[str, Path],
    target_dataset: str = "dictionary",
    conflict_resolution: str = "skip",
) -> ImportReport:
    """Import and validate records from an external file into GojriLang lexicon storage.

    Args:
        filepath: Path to the input file (.json, .jsonl, .csv).
        target_dataset: Target dataset ('dictionary').
        conflict_resolution: 'skip', 'overwrite', or 'fail'.

    Returns:
        ImportReport instance with counts and results.

    Raises:
        DatasetValidationError: If the file is malformed or validation fails in 'fail' mode.
    """
    report = validate(filepath, dataset_type=target_dataset)
    if not report.is_valid:
        raise DatasetValidationError(
            f"Validation failed for '{filepath}' with {len(report.errors)} error(s).",
            errors=report.errors,
        )

    path = Path(filepath)
    records = _read_records_from_file(path)

    # Check against bundled dictionary
    existing_ids = {e["id"] for e in load_dictionary_entries()}
    imported = 0
    skipped = 0
    overwritten = 0
    errors: List[str] = []

    for r in records:
        r_id = r.get("id")
        if r_id in existing_ids:
            if conflict_resolution == "fail":
                raise DatasetValidationError(f"Conflicting record ID '{r_id}' found in target dataset.")
            elif conflict_resolution == "overwrite":
                overwritten += 1
            else:  # skip
                skipped += 1
        else:
            imported += 1
            existing_ids.add(r_id)

    return ImportReport(
        imported_count=imported,
        skipped_count=skipped,
        overwritten_count=overwritten,
        errors=errors,
    )


def export_file(
    filepath: Union[str, Path],
    dataset_name: str = "dictionary",
    fmt: str = "auto",
) -> Path:
    """Export bundled or registered datasets to JSON, JSONL, or CSV.

    Args:
        filepath: Destination path.
        dataset_name: Dataset name ('dictionary', 'grammar', 'culture', 'translation', 'dialects', 'books').
        fmt: File format ('auto', 'json', 'jsonl', 'csv').

    Returns:
        Path to the exported file.
    """
    out_path = Path(filepath)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "auto":
        ext = out_path.suffix.lower()
        if ext == ".jsonl":
            fmt = "jsonl"
        elif ext == ".csv":
            fmt = "csv"
        else:
            fmt = "json"

    # Retrieve dataset items
    data_name = dataset_name.lower().strip()
    if data_name == "dictionary":
        items = load_dictionary_entries()
    elif data_name == "grammar":
        items = load_grammar_rules_raw().get("rules", [])
    elif data_name == "culture":
        items = load_cultural_data_raw().get("items", [])
    elif data_name == "translation":
        items = load_translation_data_raw().get("phrases", [])
    elif data_name == "dialects":
        items = load_dialects_raw().get("profiles", [])
    elif data_name == "books":
        items = load_books_raw().get("books", [])
    else:
        raise ValueError(f"Unknown dataset name '{dataset_name}'.")

    wrapper_key_map = {
        "dictionary": "entries",
        "grammar": "rules",
        "culture": "items",
        "translation": "phrases",
        "dialects": "profiles",
        "books": "books",
    }
    wrapper_key = wrapper_key_map.get(data_name, data_name)

    if fmt == "json":
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({wrapper_key: items}, f, ensure_ascii=False, indent=2)
    elif fmt == "jsonl":
        with open(out_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    elif fmt == "csv":
        if not items:
            with open(out_path, "w", encoding="utf-8", newline="") as f:
                f.write("")
        else:
            # Flatten top-level keys
            all_keys = sorted(list({k for item in items for k in item.keys()}))
            with open(out_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_keys)
                writer.writeheader()
                for item in items:
                    # Stringify non-scalar values
                    row = {
                        k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
                        for k, v in item.items()
                    }
                    writer.writerow(row)
    else:
        raise ValueError(f"Unsupported format '{fmt}'.")

    return out_path
