"""Numerical counting and ordinal system for Gojri (Gujari).

Provides verified cardinal and ordinal word generation and expression parsing
for numbers 0 to 100 based on published grammatical field studies
(J.C. Sharma 1982, pp. 62-67; Wayne Losey 2002; Grierson 1908).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from gojrilang.exceptions import UnsupportedNumberRangeError
from gojrilang.normalize import normalize_for_search

# Cardinal numbers 0 to 100 (Roman, Perso-Arabic, Devanagari)
CARDINALS: Dict[int, Tuple[str, str, str]] = {
    0: ("sifar", "صفر", "सिफ़र"),
    1: ("hik", "ہک", "हिक"),
    2: ("do", "دو", "दो"),
    3: ("traī", "ترئے", "त्रै"),
    4: ("chār", "چار", "चार"),
    5: ("panj", "پنج", "पंज"),
    6: ("chheh", "چھ", "छह"),
    7: ("sat", "ست", "सत"),
    8: ("aṭh", "اٹھ", "अठ"),
    9: ("nau", "نو", "नौ"),
    10: ("das", "دس", "दस"),
    11: ("yārā̃", "یاراں", "याराँ"),
    12: ("bārā̃", "باراں", "बाराँ"),
    13: ("terā̃", "تیراں", "तेराँ"),
    14: ("chaudā̃", "چوداں", "चौदाँ"),
    15: ("pandrā̃", "پندراں", "पन्दराँ"),
    16: ("solā̃", "سولاں", "सोलाँ"),
    17: ("satārā̃", "ستاراں", "सताराँ"),
    18: ("aṭhārā̃", "اٹھاراں", "अठाराँ"),
    19: ("unīh", "اُنیہہ", "उनीह"),
    20: ("vīh", "ویہہ", "वीह"),
    21: ("ikkī", "اکی", "इक्की"),
    22: ("bāī", "بائی", "बाई"),
    23: ("teī", "تئی", "तेई"),
    24: ("chaubī", "چوبی", "चौबी"),
    25: ("pachhī", "پچھی", "पच्छी"),
    26: ("chhabī", "چھبی", "छब्बी"),
    27: ("satāī", "ستائی", "सताई"),
    28: ("aṭhāī", "اٹھائی", "अठाई"),
    29: ("unattrī", "اُنتری", "उनत्ती"),
    30: ("trīh", "تریہہ", "त्रीह"),
    31: ("ikattrī", "اکتری", "इकत्ती"),
    32: ("battarī", "بتری", "बत्ती"),
    33: ("tetarī", "تتری", "तेत्ती"),
    34: ("chautrī", "چوتری", "चौंती"),
    35: ("paintarī", "پینتری", "पैंती"),
    36: ("chhattarī", "چھتری", "छत्ती"),
    37: ("saitattrī", "سینتری", "सैंती"),
    38: ("aṭhattrī", "اٹھتری", "अठत्ती"),
    39: ("unchālī", "اُنتالی", "उनतालीस"),
    40: ("chālīh", "چالیہہ", "चालीह"),
    41: ("iktālī", "اکتالی", "इकतालीस"),
    42: ("batālī", "بتالی", "बयालीस"),
    43: ("tertālī", "ترتالی", "तेतालीस"),
    44: ("chautālī", "چوتالی", "चौवालीस"),
    45: ("paintālī", "پینتالی", "पैंतालीस"),
    46: ("chhatālī", "چھتالی", "छियालीस"),
    47: ("saitālī", "سیتالی", "सैंतालीस"),
    48: ("aṭhtālī", "اٹھتالی", "अड़तालीस"),
    49: ("unanjā", "اُنانجا", "उनचास"),
    50: ("panjāh", "پنجاہ", "पंजाह"),
    51: ("ikvanjā", "اکونجا", "इक्यावन"),
    52: ("bāvanjā", "باونجا", "बावन"),
    53: ("terwanjā", "ترونجا", "तिरपन"),
    54: ("churanjā", "چورنجا", "चौवन"),
    55: ("pachpanjā", "پچپنجا", "पचपन"),
    56: ("chhavanjā", "چھونجا", "छप्पन"),
    57: ("satvanjā", "ستونجا", "सत्तावन"),
    58: ("aṭhvanjā", "اٹھونجا", "अट्ठावन"),
    59: ("unaṭh", "اُناٹھ", "उनसठ"),
    60: ("saṭh", "ساٹھ", "साठ"),
    61: ("ikāhaṭ", "اکاہٹ", "इकसठ"),
    62: ("bāhaṭ", "باہٹ", "बासठ"),
    63: ("trehaṭ", "تریہٹ", "तिरसठ"),
    64: ("chauhaṭ", "چوہٹ", "चौंसठ"),
    65: ("painhaṭ", "پینسٹھ", "पैंसठ"),
    66: ("chhehaṭ", "چھیسٹھ", "छियासठ"),
    67: ("satāhaṭ", "ستاہٹ", "सरसठ"),
    68: ("aṭhāhaṭ", "اٹھاہٹ", "अड़सठ"),
    69: ("unhattar", "اُنہتر", "उनहत्तर"),
    70: ("sattar", "ستر", "सत्तर"),
    71: ("ikhattar", "اکہتر", "इकत्तर"),
    72: ("bahattar", "بہتر", "बहत्तर"),
    73: ("tihattar", "تہتر", "तिहत्तर"),
    74: ("chauhattar", "چوہتر", "चौहत्तर"),
    75: ("pachhattar", "پچھتر", "पचहत्तर"),
    76: ("chhahattar", "چھہتر", "छिहत्तर"),
    77: ("sathattar", "ستھتر", "सतहत्तर"),
    78: ("aṭhhattar", "اٹھہتر", "अठहत्तर"),
    79: ("unāsī", "اُنّاسی", "उनासी"),
    80: ("assī", "اسی", "अस्सी"),
    81: ("ikyāsī", "اکیّاسی", "इक्यासी"),
    82: ("bayāsī", "بیّاسی", "बयासी"),
    83: ("tirāsī", "تراسی", "तिरासी"),
    84: ("chaurāsī", "چوراسی", "चौरासी"),
    85: ("pachāsī", "پچاسی", "पचासी"),
    86: ("chhyāsī", "چھیاسی", "छियासी"),
    87: ("satāsī", "ستاسی", "सत्तासी"),
    88: ("aṭhāsī", "اٹھاسی", "अट्ठासी"),
    89: ("navāsī", "نواسی", "नवासी"),
    90: ("nabbe", "نبے", "नब्बे"),
    91: ("ikānvē", "اکانوے", "इक्यानवे"),
    92: ("bānvē", "بانوے", "बानवे"),
    93: ("tirānvē", "ترانوے", "तिरानवे"),
    94: ("chaurānvē", "چورانوے", "चौरानवे"),
    95: ("pachānvē", "پچانوے", "पचानवे"),
    96: ("chhyānvē", "چھیانوے", "छियानवे"),
    97: ("satānvē", "ستانوے", "सप्तानवे"),
    98: ("aṭhānvē", "اٹھانوے", "अट्ठानवे"),
    99: ("naṛīnvē", "نڑانوے", "निन्यानवे"),
    100: ("sau", "سو", "सौ"),
}

# Special ordinals 1 to 6
SPECIAL_ORDINALS: Dict[int, Dict[str, Tuple[str, str, str]]] = {
    1: {
        "masculine": ("pehlo", "پہلو", "पहलो"),
        "feminine": ("pehlī", "پہلی", "पहली"),
    },
    2: {
        "masculine": ("dūjo", "دوجو", "दूजो"),
        "feminine": ("dūjī", "دوجی", "दूजी"),
    },
    3: {
        "masculine": ("tījo", "تیجو", "तीजो"),
        "feminine": ("tījī", "تیجی", "तीजी"),
    },
    4: {
        "masculine": ("chautho", "چوتھو", "चौथो"),
        "feminine": ("chauthī", "چوتھی", "चौथी"),
    },
    5: {
        "masculine": ("panjvo", "پنجوو", "पंजवो"),
        "feminine": ("panjvī", "پنجوی", "पंजवी"),
    },
    6: {
        "masculine": ("chhaṭho", "چھٹھو", "छठो"),
        "feminine": ("chhaṭhī", "چھٹھی", "छठी"),
    },
}

# Reverse lookup index for parse_words
_WORD_TO_NUMBER: Dict[str, int] = {}
for num, (rom, pa, dev) in CARDINALS.items():
    _WORD_TO_NUMBER[rom.lower()] = num
    _WORD_TO_NUMBER[normalize_for_search(rom)] = num
    _WORD_TO_NUMBER[pa] = num
    _WORD_TO_NUMBER[dev] = num
    # Alternate variants for common numbers
    if num == 1:
        _WORD_TO_NUMBER["ek"] = 1
        _WORD_TO_NUMBER["اک"] = 1
        _WORD_TO_NUMBER["इक"] = 1
    elif num == 3:
        _WORD_TO_NUMBER["trae"] = 3
        _WORD_TO_NUMBER["tin"] = 3
        _WORD_TO_NUMBER["تین"] = 3
        _WORD_TO_NUMBER["तीन"] = 3
    elif num == 20:
        _WORD_TO_NUMBER["vih"] = 20
        _WORD_TO_NUMBER["ویہ"] = 20
    elif num == 50:
        _WORD_TO_NUMBER["panjah"] = 50
        _WORD_TO_NUMBER["پنجا"] = 50
    elif num == 100:
        _WORD_TO_NUMBER["so"] = 100
        _WORD_TO_NUMBER["सै"] = 100


def to_words(number: int, script: str = "roman") -> str:
    """Convert an integer in range [0, 100] to its verified Gojri word representation.

    Args:
        number: Integer between 0 and 100 inclusive.
        script: Target script ('roman', 'perso-arabic', 'devanagari').

    Returns:
        The Gojri number string.

    Raises:
        UnsupportedNumberRangeError: If number is outside the authenticated [0, 100] range.
    """
    if number < 0 or number > 100:
        raise UnsupportedNumberRangeError(number, 0, 100)

    rom, pa, dev = CARDINALS[number]
    s_clean = script.lower().strip()
    if "perso" in s_clean or "arabic" in s_clean or "urdu" in s_clean:
        return pa
    if "devanagari" in s_clean or "hindi" in s_clean:
        return dev
    return rom


def parse_words(expression: str) -> int:
    """Parse a Gojri number expression (in any script or romanized form) into an integer.

    Args:
        expression: Gojri number in words (e.g., 'hik', 'vīh', 'پنجاہ', 'हिक').

    Returns:
        Parsed integer value.

    Raises:
        ValueError: If the expression cannot be parsed into a known Gojri number.
    """
    if not expression or not expression.strip():
        raise ValueError("Cannot parse empty number expression.")

    clean = expression.strip()
    low = clean.lower()
    norm = normalize_for_search(clean)

    if clean in _WORD_TO_NUMBER:
        return _WORD_TO_NUMBER[clean]
    if low in _WORD_TO_NUMBER:
        return _WORD_TO_NUMBER[low]
    if norm in _WORD_TO_NUMBER:
        return _WORD_TO_NUMBER[norm]

    # Try digit string directly
    if clean.isdigit():
        val = int(clean)
        if 0 <= val <= 100:
            return val

    raise ValueError(f"Unrecognised Gojri number expression: '{expression}'")


def ordinal_to_words(
    number: int,
    gender: str = "masculine",
    script: str = "roman",
) -> str:
    """Generate the Gojri ordinal form for a number in range [1, 100].

    Gojri ordinals exhibit gender agreement:
    - 1st: pehlo (m) / pehlī (f)
    - 2nd: dūjo (m) / dūjī (f)
    - 3rd: tījo (m) / tījī (f)
    - 4th: chautho (m) / chauthī (f)
    - 5th+: root + vo (m) / vī (f)

    Args:
        number: Integer between 1 and 100.
        gender: 'masculine' or 'feminine'.
        script: 'roman', 'perso-arabic', 'devanagari'.

    Returns:
        Ordinal word string.

    Raises:
        UnsupportedNumberRangeError: If number is not in range [1, 100].
    """
    if number < 1 or number > 100:
        raise UnsupportedNumberRangeError(number, 1, 100)

    g_clean = gender.lower().strip()
    is_fem = g_clean.startswith("f")

    s_clean = script.lower().strip()
    is_pa = "perso" in s_clean or "arabic" in s_clean or "urdu" in s_clean
    is_dev = "devanagari" in s_clean or "hindi" in s_clean

    # Check special irregular ordinals 1 to 6
    if number in SPECIAL_ORDINALS:
        target_g = "feminine" if is_fem else "masculine"
        rom, pa, dev = SPECIAL_ORDINALS[number][target_g]
        if is_pa:
            return pa
        if is_dev:
            return dev
        return rom

    # Regular formation for 7..100: base + vo / vī
    base_rom, base_pa, base_dev = CARDINALS[number]
    if is_pa:
        suffix = "وی" if is_fem else "وو"
        return f"{base_pa}{suffix}"
    if is_dev:
        suffix = "वी" if is_fem else "वो"
        return f"{base_dev}{suffix}"

    suffix = "vī" if is_fem else "vo"
    return f"{base_rom}{suffix}"

