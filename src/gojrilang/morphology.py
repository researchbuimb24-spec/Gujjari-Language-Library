"""Morphological analysis and evidence-based paradigm generation for Gojri.

Provides stem analysis, documented affix detection, and inflectional paradigms
derived from J.C. Sharma (1982) and Wayne Losey (2002).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.dictionary import lookup
from gojrilang.exceptions import GojriLangError
from gojrilang.normalize import detect_script, normalize, normalize_for_search


SUPPORTED_PARADIGM_CATEGORIES = {
    "marked_masculine_noun",
    "marked_feminine_noun",
    "regular_verb",
}

DOCUMENTED_AFFIXES = [
    {
        "affix": "-o",
        "type": "suffix",
        "function": "Masculine singular nominal/adjectival marker",
        "script": "roman / perso-arabic (و)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_NOUN_01",
    },
    {
        "affix": "-i",
        "type": "suffix",
        "function": "Feminine singular nominal/adjectival marker",
        "script": "roman / perso-arabic (ی)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_NOUN_02",
    },
    {
        "affix": "-e",
        "type": "suffix",
        "function": "Masculine plural direct / singular oblique marker",
        "script": "roman / perso-arabic (ے)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_NOUN_01",
    },
    {
        "affix": "-yā̃ / -ā̃",
        "type": "suffix",
        "function": "Plural oblique nominal suffix",
        "script": "roman / perso-arabic (یاں / آں)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_NOUN_01",
    },
    {
        "affix": "-ṇo / -no",
        "type": "suffix",
        "function": "Infinitive / citation verbal suffix",
        "script": "roman / perso-arabic (ݨو / نو)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_VERB_01",
    },
    {
        "affix": "-to / -ti",
        "type": "suffix",
        "function": "Present habitual / imperfective participle",
        "script": "roman / perso-arabic (تو / تی)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_TAM_01",
    },
    {
        "affix": "-go / -ga / -gi",
        "type": "suffix",
        "function": "Future tense suffix",
        "script": "roman / perso-arabic (گو / گا / گی)",
        "source": "SHARMA_1982",
        "rule_id": "RULE_TAM_02",
    },
]


@dataclass
class WordAnalysis:
    """Detailed morphological analysis of a Gojri word token."""

    original: str
    normalized: str
    script: str
    lemma: Optional[str]
    pos: Optional[str]
    stem: Optional[str]
    affixes: List[Dict[str, str]]
    gender: Optional[str]
    number: Optional[str]
    case: Optional[str]
    dialect_notes: Optional[str]
    verification_status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        parts = [f"Token: '{self.original}'"]
        if self.lemma:
            parts.append(f"Lemma: '{self.lemma}'")
        if self.pos:
            parts.append(f"POS: {self.pos}")
        if self.gender:
            parts.append(f"Gender: {self.gender}")
        if self.number:
            parts.append(f"Number: {self.number}")
        if self.case:
            parts.append(f"Case: {self.case}")
        if self.stem:
            parts.append(f"Stem: '{self.stem}'")
        parts.append(f"[{self.verification_status}]")
        return " | ".join(parts)


def list_documented_affixes() -> List[Dict[str, str]]:
    """Return the list of validated Gojri affixes."""
    return list(DOCUMENTED_AFFIXES)


def analyze_word(word: str) -> WordAnalysis:
    """Analyze the morphological structure of a Gojri word.

    Performs dictionary lookup first, then evaluates documented inflectional
    and derivational suffixes according to J.C. Sharma (1982).

    Args:
        word: A Gojri word string.

    Returns:
        WordAnalysis dataclass instance.
    """
    if not word or not word.strip():
        return WordAnalysis(
            original="",
            normalized="",
            script="unknown",
            lemma=None,
            pos=None,
            stem=None,
            affixes=[],
            gender=None,
            number=None,
            case=None,
            dialect_notes=None,
            verification_status="provisional",
        )

    norm = normalize(word)
    script = detect_script(norm)

    # 1. Direct dictionary lookup
    dict_entry = lookup(word)
    if dict_entry:
        return WordAnalysis(
            original=word,
            normalized=norm,
            script=script,
            lemma=dict_entry.word,
            pos=dict_entry.pos,
            stem=dict_entry.word[:-1] if dict_entry.word.endswith(("و", "ی", "ے", "o", "i", "e")) else dict_entry.word,
            affixes=[],
            gender=dict_entry.gender,
            number="singular",
            case="direct",
            dialect_notes=dict_entry.dialect,
            verification_status="verified",
        )

    # 2. Rule-based morphological segmentation on unindexed tokens
    clean = normalize_for_search(norm)
    stem: Optional[str] = None
    affixes: List[Dict[str, str]] = []
    gender: Optional[str] = None
    number: Optional[str] = None
    case: Optional[str] = None
    pos: Optional[str] = None

    # Perso-Arabic suffixes
    if script == "perso-arabic":
        if norm.endswith("یاں"):
            stem = norm[:-3]
            affixes.append({"affix": "-یاں", "type": "suffix", "function": "plural oblique / feminine plural", "rule_id": "RULE_NOUN_01"})
            number = "plural"
            case = "oblique"
            verification_status = "attested_pattern"
        elif norm.endswith("و"):
            stem = norm[:-1]
            affixes.append({"affix": "-و", "type": "suffix", "function": "masculine singular direct", "rule_id": "RULE_NOUN_01"})
            gender = "masculine"
            number = "singular"
            case = "direct"
            verification_status = "attested_pattern"
        elif norm.endswith("ی"):
            stem = norm[:-1]
            affixes.append({"affix": "-ی", "type": "suffix", "function": "feminine singular", "rule_id": "RULE_NOUN_02"})
            gender = "feminine"
            number = "singular"
            case = "direct"
            verification_status = "attested_pattern"
        elif norm.endswith("ے"):
            stem = norm[:-1]
            affixes.append({"affix": "-ے", "type": "suffix", "function": "masculine plural direct or singular oblique", "rule_id": "RULE_NOUN_01"})
            gender = "masculine"
            case = "oblique_or_plural"
            verification_status = "attested_pattern"
        elif norm.endswith("ݨو") or norm.endswith("نو"):
            stem = norm[:-2]
            affixes.append({"affix": "-ݨو/-نو", "type": "suffix", "function": "verbal infinitive", "rule_id": "RULE_VERB_01"})
            pos = "verb"
            verification_status = "attested_pattern"
        else:
            stem = norm
            verification_status = "unsegmented"

    # Romanized suffixes
    elif script == "latin":
        low = norm.lower()
        if low.endswith("iyā̃") or low.endswith("yā̃") or low.endswith("yañ") or low.endswith("añ"):
            stem = low.split("y")[0] if "y" in low else low[:-2]
            affixes.append({"affix": "-yā̃", "type": "suffix", "function": "plural oblique / feminine plural", "rule_id": "RULE_NOUN_01"})
            number = "plural"
            case = "oblique"
            verification_status = "attested_pattern"
        elif low.endswith("o"):
            stem = low[:-1]
            affixes.append({"affix": "-o", "type": "suffix", "function": "masculine singular direct", "rule_id": "RULE_NOUN_01"})
            gender = "masculine"
            number = "singular"
            case = "direct"
            verification_status = "attested_pattern"
        elif low.endswith("i") or low.endswith("ī"):
            stem = low[:-1]
            affixes.append({"affix": "-i", "type": "suffix", "function": "feminine singular", "rule_id": "RULE_NOUN_02"})
            gender = "feminine"
            number = "singular"
            case = "direct"
            verification_status = "attested_pattern"
        elif low.endswith("e"):
            stem = low[:-1]
            affixes.append({"affix": "-e", "type": "suffix", "function": "masculine plural direct / singular oblique", "rule_id": "RULE_NOUN_01"})
            gender = "masculine"
            case = "oblique_or_plural"
            verification_status = "attested_pattern"
        elif low.endswith("ṇo") or low.endswith("no"):
            stem = low[:-2]
            affixes.append({"affix": "-ṇo/-no", "type": "suffix", "function": "verbal infinitive", "rule_id": "RULE_VERB_01"})
            pos = "verb"
            verification_status = "attested_pattern"
        else:
            stem = norm
            verification_status = "unsegmented"
    else:
        stem = norm
        verification_status = "unsegmented"

    # Attempt to locate underlying lemma from recovered stem
    lemma = None
    if stem:
        possible_lemma = lookup(stem + "و") or lookup(stem + "o") or lookup(stem)
        if possible_lemma:
            lemma = possible_lemma.word
            if not pos:
                pos = possible_lemma.pos

    return WordAnalysis(
        original=word,
        normalized=norm,
        script=script,
        lemma=lemma,
        pos=pos,
        stem=stem,
        affixes=affixes,
        gender=gender,
        number=number,
        case=case,
        dialect_notes="General Gojri morphological rules applied",
        verification_status=verification_status,
    )


def generate_forms(
    root: str,
    category: str,
    dialect: str = "general",
) -> Dict[str, str]:
    """Generate authenticated inflectional paradigm forms for a verified root/stem.

    Only productive paradigms documented in published Gojri grammars are generated.
    Speculative paradigms are rejected.

    Supported categories:
      - 'marked_masculine_noun'
      - 'marked_feminine_noun'
      - 'regular_verb'

    Args:
        root: The nominal stem or verbal root (e.g., 'ghoṛ', 'گھوڑ', 'bakr', 'بکر', 'jā', 'kar').
        category: Paradigm category.
        dialect: Dialect variation ('general', 'jammu_kashmir', 'eastern', 'western').

    Returns:
        Dictionary mapping grammatical slots to generated forms.

    Raises:
        GojriLangError: If category is unsupported or root is invalid.
    """
    if not root or not root.strip():
        raise GojriLangError("Root cannot be empty.")

    cat_clean = category.strip().lower()
    if cat_clean not in SUPPORTED_PARADIGM_CATEGORIES:
        raise GojriLangError(
            f"Unsupported paradigm category '{category}'. Supported categories: "
            f"{', '.join(sorted(list(SUPPORTED_PARADIGM_CATEGORIES)))}"
        )

    clean_root = root.strip()
    script = detect_script(clean_root)

    # 1. Marked Masculine Nouns (e.g. ghoṛo, bakro)
    if cat_clean == "marked_masculine_noun":
        if script == "perso-arabic":
            # If input passed as lemma ending in و, strip it to extract base stem
            stem = clean_root[:-1] if clean_root.endswith("و") else clean_root
            return {
                "direct_singular": f"{stem}و",
                "direct_plural": f"{stem}ے",
                "oblique_singular": f"{stem}ے",
                "oblique_plural": f"{stem}یاں",
            }
        else:
            stem = clean_root[:-1] if clean_root.lower().endswith("o") else clean_root
            return {
                "direct_singular": f"{stem}o",
                "direct_plural": f"{stem}e",
                "oblique_singular": f"{stem}e",
                "oblique_plural": f"{stem}yā̃",
            }

    # 2. Marked Feminine Nouns (e.g. ghoṛi, bakri)
    if cat_clean == "marked_feminine_noun":
        if script == "perso-arabic":
            stem = clean_root[:-1] if clean_root.endswith("ی") else clean_root
            return {
                "direct_singular": f"{stem}ی",
                "direct_plural": f"{stem}یاں",
                "oblique_singular": f"{stem}ی",
                "oblique_plural": f"{stem}یاں",
            }
        else:
            stem = clean_root[:-1] if clean_root.lower().endswith(("i", "ī")) else clean_root
            return {
                "direct_singular": f"{stem}i",
                "direct_plural": f"{stem}iyā̃",
                "oblique_singular": f"{stem}i",
                "oblique_plural": f"{stem}iyā̃",
            }

    # 3. Regular Verbs (e.g. kar, jā)
    if cat_clean == "regular_verb":
        if script == "perso-arabic":
            stem = clean_root
            # Infinitive takes ݨو or نو
            inf_suffix = "نو" if stem.endswith(("ن", "ت", "د")) else "ݨو"
            return {
                "infinitive": f"{stem}{inf_suffix}",
                "habitual_masc_sg": f"{stem}تو",
                "habitual_masc_pl": f"{stem}تے",
                "habitual_fem_sg": f"{stem}تی",
                "future_masc_sg": f"{stem}و گو",
                "future_masc_pl": f"{stem}و گا",
            }
        else:
            stem = clean_root
            inf_suffix = "no" if stem.endswith(("n", "t", "d")) else "ṇo"
            return {
                "infinitive": f"{stem}{inf_suffix}",
                "habitual_masc_sg": f"{stem}to",
                "habitual_masc_pl": f"{stem}te",
                "habitual_fem_sg": f"{stem}ti",
                "future_masc_sg": f"{stem}o go",
                "future_masc_pl": f"{stem}o gā",
            }

    raise GojriLangError(f"Generation for '{category}' is not implemented.")


def lemmatize(word: str) -> Optional[str]:
    """Retrieve the base canonical lemma for an inflected or variant Gojri word token.

    Checks the verified dictionary first, then applies morphological detachment
    of documented inflectional affixes (J.C. Sharma 1982).

    Args:
        word: A Gojri word token in Perso-Arabic, Devanagari, or Roman script.

    Returns:
        The canonical lemma string if resolved, or None if empty.
    """
    if not word or not word.strip():
        return None

    clean_w = word.strip()
    analysis = analyze_word(clean_w)
    if analysis.lemma:
        return analysis.lemma

    if analysis.stem and analysis.stem != clean_w:
        # Check if stem or reconstructed citation form exists in dictionary
        is_pa = analysis.script == "perso-arabic"
        candidates = [
            analysis.stem + ("و" if is_pa else "o"),
            analysis.stem + ("ی" if is_pa else "i"),
            analysis.stem + ("ݨو" if is_pa else "ṇo"),
            analysis.stem,
        ]
        for c in candidates:
            entry = lookup(c)
            if entry:
                return entry.word

        return analysis.stem

    return analysis.normalized or clean_w


