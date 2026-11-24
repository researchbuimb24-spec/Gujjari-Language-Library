"""Gojri oral folklore, riddles (Pahaṇḍi), and pastoral traditions subsystem."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.culture import CulturalItem, search_culture
from gojrilang.normalize import normalize_for_search


@dataclass
class Riddle:
    """A traditional Gojri riddle (Pahaṇḍi / Bujhārat)."""

    id: str
    question_perso_arabic: str
    question_devanagari: str
    question_roman: str
    answer_gojri: str
    answer_en: str
    translation_en: str
    cultural_context: str
    source: str = "JKAACL Folklore Archives"

    @property
    def answer_english(self) -> str:
        return self.answer_en

    @property
    def cultural_clue(self) -> str:
        return self.cultural_context

    @property
    def region(self) -> str:
        return "Western Himalayas / J&K"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PastoralCustom:
    """A documented pastoral transhumance custom, ritual, or community celebration."""

    id: str
    title: str
    category: str  # transhumance, festival, wedding, seasonal
    description_en: str
    description_gojri: str
    season_or_timing: str
    region: str
    source: str = "JKAACL Cultural Documentation"

    @property
    def name_gojri(self) -> str:
        return self.title

    @property
    def name_english(self) -> str:
        return self.title

    @property
    def season(self) -> str:
        return self.season_or_timing

    @property
    def significance(self) -> str:
        return self.description_en

    @property
    def description(self) -> str:
        return self.description_en

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_RIDDLES_CORPUS: List[Riddle] = [
    Riddle(
        id="RIDDLE_01",
        question_perso_arabic="نکی جئی کٹیا، لال لال چولا، اندر بیٹھیو گوات رو گولا۔",
        question_devanagari="निकी जई कुटिया, लाल लाल चोला, अन्दर बैठ्यो ग्वाल रो गोला।",
        question_roman="Nikī jaī kuṭiyā, lāl lāl cholā, andar baiṭhyo gwāl ro golā.",
        answer_gojri="انار (अनार / anār)",
        answer_en="Pomegranate",
        translation_en="A tiny little cottage with a bright red robe, inside sits the herdsman's pearl.",
        cultural_context="Popular pastoral riddle recited during winter hearth gatherings.",
    ),
    Riddle(
        id="RIDDLE_02",
        question_perso_arabic="ہک ڈانگ ایسی، جیدے بارہ بند، ہر بند تے ہک ہک چن۔",
        question_devanagari="हिक डांग ऐसी, जेदे बारह बन्द, हर बन्द ते हिक हिक चन।",
        question_roman="Hik ḍāng aisī, jede bārah band, har band te hik hik chan.",
        answer_gojri="ورھو تے بارہ مہینے (वरहो ते बारह महीने / varho te bārah mahīne)",
        answer_en="A year and its twelve months",
        translation_en="A single walking staff that has twelve joints, and on each joint shines a moon.",
        cultural_context="Astronomical pastoral riddle teaching seasonal transhumance calendar to children.",
    ),
]

_CUSTOMS_CORPUS: List[PastoralCustom] = [
    PastoralCustom(
        id="CUSTOM_BAHAK_CHAL",
        title="Bahak Chal (Ascent to Alpine Summer Pastures)",
        category="transhumance",
        description_en="The festive annual migration ritual in Baisakh where Gujjar & Bakarwal pastoral families set out with horses and cattle to high alpine ridges.",
        description_gojri="بیساکھ ما باہکاں وال ٹرݨ دی رسم، مال ڈنگر نا سجا کے نوی گھاہ وال لے جانا۔",
        season_or_timing="Spring / Baisakh (April-May)",
        region="Pir Panjal, Shivalik, Hazara",
    ),
    PastoralCustom(
        id="CUSTOM_DHOONI_BAAL",
        title="Dhooni Baal (Lighting the Winter Hearth Fire)",
        category="seasonal",
        description_en="The communal gathering around the stone cottage hearth in winter months (Poh) where elders recite folk dastans and heroic Chhaint.",
        description_gojri="سیالے دے مہینے کٹیا ما دھونی بال کے بزرگاں کن کہانیاں سنݨ دی روایت۔",
        season_or_timing="Winter / Poh-Magh (December-January)",
        region="Western Himalayas / Jammu & Kashmir",
    ),
]


def list_riddles() -> List[Riddle]:
    """Return documented Gojri riddles (Pahaṇḍi)."""
    return list(_RIDDLES_CORPUS)


def get_riddle(riddle_id: str) -> Optional[Riddle]:
    """Retrieve a riddle by its ID."""
    clean_id = riddle_id.strip().lower()
    for r in _RIDDLES_CORPUS:
        if r.id.lower() == clean_id:
            return r
    return None


def list_customs(category: Optional[str] = None) -> List[PastoralCustom]:
    """List pastoral customs, rituals, and seasonal celebrations."""
    results = []
    for c in _CUSTOMS_CORPUS:
        if category and c.category.lower() != category.strip().lower():
            continue
        results.append(c)
    return results


def search_folklore(query: str) -> Dict[str, Any]:
    """Search across traditional riddles, customs, and cultural folklore."""
    q_norm = normalize_for_search(query)
    matched_riddles = [
        r.to_dict() for r in _RIDDLES_CORPUS
        if q_norm in normalize_for_search(r.question_perso_arabic)
        or q_norm in normalize_for_search(r.question_roman)
        or q_norm in normalize_for_search(r.answer_en)
        or q_norm in normalize_for_search(r.translation_en)
    ]
    matched_customs = [
        c.to_dict() for c in _CUSTOMS_CORPUS
        if q_norm in normalize_for_search(c.title)
        or q_norm in normalize_for_search(c.description_en)
        or q_norm in normalize_for_search(c.description_gojri)
    ]
    cult_items = [
        i.to_dict() for i in search_culture(query, category="folklore")
    ]
    return {
        "query": query,
        "riddles": matched_riddles,
        "customs": matched_customs,
        "cultural_folklore": cult_items,
        "total_matches": len(matched_riddles) + len(matched_customs) + len(cult_items),
    }
