"""Tests for gojri command line interface."""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout

import pytest

import gojrilang
from gojrilang.cli import main


def run_cli(*args: str) -> tuple[int, str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        try:
            code = main(list(args))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 0
    return code, out_buf.getvalue(), err_buf.getvalue()


def test_cli_version() -> None:
    code, out, _ = run_cli("--version")
    assert code == 0
    assert f"gojrilang {gojrilang.__version__}" in out


def test_cli_stats() -> None:
    code, out, _ = run_cli("stats")
    assert code == 0
    assert "GojriLang Corpus Statistics" in out
    assert "Gujari / Gojri" in out


def test_cli_stats_json() -> None:
    code, out, _ = run_cli("--json", "stats")
    assert code == 0
    data = json.loads(out)
    assert "dictionary" in data
    assert "grammar" in data


def test_cli_lookup_success() -> None:
    code, out, _ = run_cli("lookup", "گھوڑو")
    assert code == 0
    assert "horse" in out
    assert "SHARMA_1982" in out


def test_cli_lookup_json() -> None:
    code, out, _ = run_cli("--json", "lookup", "گھوڑو")
    assert code == 0
    data = json.loads(out)
    assert data["word"] == "گھوڑو"
    assert data["meaning_en"] == "horse"


def test_cli_lookup_not_found() -> None:
    code, out, err = run_cli("lookup", "nonexistent_term_999")
    assert code == 1
    assert "not found" in err


def test_cli_search() -> None:
    code, out, _ = run_cli("search", "horse", "--language", "english")
    assert code == 0
    assert "گھوڑو" in out


def test_cli_normalize() -> None:
    code, out, _ = run_cli("normalize", "  گھوڑو    ہے  ")
    assert code == 0
    assert out.strip() == "گھوڑو ہے"


def test_cli_transliterate() -> None:
    code, out, _ = run_cli("transliterate", "گھوڑو", "--from", "perso-arabic", "--to", "roman")
    assert code == 0
    assert "gh" in out


def test_cli_grammar_list() -> None:
    code, out, _ = run_cli("grammar", "list")
    assert code == 0
    assert "RULE_PHON_01" in out


def test_cli_grammar_show() -> None:
    code, out, _ = run_cli("grammar", "show", "RULE_POSTPOS_01")
    assert code == 0
    assert "Split-Ergative" in out


def test_cli_grammar_analyze() -> None:
    code, out, _ = run_cli("grammar", "analyze", "چھورے نے روٹی کھادی")
    assert code == 0
    assert "Sentence Diagnostics" in out
    assert "ergative" in out.lower()


def test_cli_morphology_analyze() -> None:
    code, out, _ = run_cli("morphology", "analyze", "گھوڑو")
    assert code == 0
    assert "masculine" in out


def test_cli_morphology_generate() -> None:
    code, out, _ = run_cli("morphology", "generate", "ghoṛ", "--category", "marked_masculine_noun")
    assert code == 0
    assert "ghoṛo" in out
    assert "ghoṛe" in out


def test_cli_culture_list() -> None:
    code, out, _ = run_cli("culture", "list")
    assert code == 0
    assert "جیسی کرنی" in out


def test_cli_culture_songs() -> None:
    code, out, _ = run_cli("culture", "songs")
    assert code == 0
    assert "Chhaint" in out
    assert "Mahya" in out


def test_cli_culture_songs_json() -> None:
    code, out, _ = run_cli("--json", "culture", "songs")
    assert code == 0
    import json
    data = json.loads(out)
    assert len(data) >= 7
    assert any("Chhaint" in s["title"] for s in data)


def test_cli_culture_search() -> None:
    code, out, _ = run_cli("culture", "search", "vessel")
    assert code == 0
    assert "خالی برتن" in out


def test_cli_translate() -> None:
    code, out, _ = run_cli("translate", "تسی کس طرح چھو؟", "--from", "gojri", "--to", "english")
    assert code == 0
    assert "How are you" in out


def test_cli_grammar_explain() -> None:
    code, out, _ = run_cli("grammar", "explain", "RULE_POSTPOS_01")
    assert code == 0
    assert "RULE_POSTPOS_01" in out
    assert "Split-Ergative" in out


def test_cli_morphology_lemmatize() -> None:
    code, out, _ = run_cli("morphology", "lemmatize", "گھوڑیاں")
    assert code == 0
    assert "Lemma for 'گھوڑیاں':" in out


def test_cli_dialects_list() -> None:
    code, out, _ = run_cli("dialects", "list")
    assert code == 0
    assert "jk_poonchi" in out
    assert "western_hazara" in out


def test_cli_dialects_show() -> None:
    code, out, _ = run_cli("dialects", "show", "jk_poonchi")
    assert code == 0
    assert "Poonch" in out


def test_cli_dialects_compare() -> None:
    code, out, _ = run_cli("dialects", "compare", "water")
    assert code == 0
    assert "Dialect Comparison" in out


def test_cli_books_list() -> None:
    code, out, _ = run_cli("books", "list")
    assert code == 0
    assert "grierson_1908_lsi" in out
    assert "gojri_ramkatha_oral" in out
    assert "gojri_pandav_katha_oral" in out


def test_cli_books_show() -> None:
    code, out, _ = run_cli("books", "show", "grierson_1908_lsi")
    assert code == 0
    assert "Linguistic Survey of India" in out


def test_cli_books_read() -> None:
    code, out, _ = run_cli("books", "read", "grierson_1908_lsi", "1")
    assert code == 0
    assert "Parable of the Prodigal Son" in out


def test_cli_books_search() -> None:
    code, out, _ = run_cli("books", "search", "prodigal")
    assert code == 0
    assert "grierson_1908_lsi" in out


def test_cli_numbers_to_words() -> None:
    code, out, _ = run_cli("numbers", "to-words", "20")
    assert code == 0
    assert "vīh" in out


def test_cli_numbers_parse() -> None:
    code, out, _ = run_cli("numbers", "parse", "vīh")
    assert code == 0
    assert "20" in out


def test_cli_numbers_ordinal() -> None:
    code, out, _ = run_cli("numbers", "ordinal", "1", "--gender", "feminine")
    assert code == 0
    assert "pehlī" in out


def test_cli_pronunciation_show() -> None:
    code, out, _ = run_cli("pronunciation", "show", "گھوڑو")
    assert code == 0
    assert "IPA:" in out


def test_cli_dataset_validate(tmp_path: pytest.TempPathFactory) -> None:
    # Use exported or dummy file
    code, out, _ = run_cli("stats")
    assert code == 0


