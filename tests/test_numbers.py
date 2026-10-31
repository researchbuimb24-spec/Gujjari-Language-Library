"""Tests for Gojri numerical counting and ordinal word generation."""

from __future__ import annotations

import pytest

from gojrilang.exceptions import UnsupportedNumberRangeError
from gojrilang.numbers import (
    ordinal_to_words,
    parse_words,
    to_words,
)


def test_to_words_boundaries_and_cardinals() -> None:
    assert to_words(0) == "sifar"
    assert to_words(1) == "hik"
    assert to_words(2) == "do"
    assert to_words(10) == "das"
    assert to_words(20) == "vīh"
    assert to_words(50) == "panjāh"
    assert to_words(100) == "sau"


def test_to_words_scripts() -> None:
    assert to_words(1, script="perso-arabic") == "ہک"
    assert to_words(1, script="devanagari") == "हिक"
    assert to_words(20, script="perso-arabic") == "ویہہ"
    assert to_words(20, script="devanagari") == "वीह"
    assert to_words(50, script="perso-arabic") == "پنجاہ"
    assert to_words(100, script="perso-arabic") == "سو"


def test_to_words_out_of_range_raises() -> None:
    with pytest.raises(UnsupportedNumberRangeError):
        to_words(-1)
    with pytest.raises(UnsupportedNumberRangeError):
        to_words(101)


def test_parse_words() -> None:
    assert parse_words("hik") == 1
    assert parse_words("ہک") == 1
    assert parse_words("हिक") == 1
    assert parse_words("vīh") == 20
    assert parse_words("panjāh") == 50
    assert parse_words("sau") == 100
    assert parse_words("42") == 42


def test_parse_words_invalid_raises() -> None:
    with pytest.raises(ValueError):
        parse_words("not_a_number_word_at_all")
    with pytest.raises(ValueError):
        parse_words("")


def test_ordinal_to_words_irregular() -> None:
    assert ordinal_to_words(1, gender="masculine") == "pehlo"
    assert ordinal_to_words(1, gender="feminine") == "pehlī"
    assert ordinal_to_words(2, gender="masculine") == "dūjo"
    assert ordinal_to_words(2, gender="feminine") == "dūjī"
    assert ordinal_to_words(3, gender="masculine") == "tījo"
    assert ordinal_to_words(4, gender="masculine") == "chautho"
    assert ordinal_to_words(5, gender="masculine") == "panjvo"
    assert ordinal_to_words(6, gender="masculine") == "chhaṭho"


def test_ordinal_to_words_regular() -> None:
    # 7th = sat + vo
    assert ordinal_to_words(7, gender="masculine") == "satvo"
    assert ordinal_to_words(7, gender="feminine") == "satvī"
    # 10th = das + vo
    assert ordinal_to_words(10, gender="masculine") == "dasvo"


def test_ordinal_out_of_range_raises() -> None:
    with pytest.raises(UnsupportedNumberRangeError):
        ordinal_to_words(0)
    with pytest.raises(UnsupportedNumberRangeError):
        ordinal_to_words(101)

