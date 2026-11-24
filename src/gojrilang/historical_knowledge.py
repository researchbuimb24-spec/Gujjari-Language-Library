"""Historical knowledge, transhumance geography, and tribal heritage subsystem for Gojri."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.normalize import normalize_for_search


@dataclass
class HistoricalPlace:
    """A geographic location, mountain pass, or cultural site significant to Gojri history."""

    id: str
    name: str
    name_gojri: str
    region: str
    altitude_m: Optional[int]
    historical_significance: str
    source: str = "Himalayan Cultural Survey / JKAACL"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TribalClan:
    """A documented Gujjar ancestral clan (Gotra / Zaat) with historical heritage."""

    name: str
    name_gojri: str
    historical_roots: str
    prominent_regions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_HISTORICAL_PLACES: List[HistoricalPlace] = [
    HistoricalPlace(
        id="place_pir_ki_gali",
        name="Pir Ki Gali (Pir Panjal Pass)",
        name_gojri="پیر کی گلی",
        region="Pir Panjal Range (Poonch-Shopian border)",
        altitude_m=3485,
        historical_significance="Historic mountain pass used for centuries by Gujjar & Bakarwal caravans during seasonal transhumant migration between the plains and Kashmir.",
    ),
    HistoricalPlace(
        id="place_wangat_baba_nagri",
        name="Wangat (Baba Nagri)",
        name_gojri="وانگت (بابا نگری)",
        region="Ganderbal, Kashmir Valley",
        altitude_m=2100,
        historical_significance="Spiritual center of Gojri literary and Sufi heritage, founded by Hazrat Mian Nizam-ud-Din Larvi (1863–1926).",
    ),
    HistoricalPlace(
        id="place_saiful_muluk",
        name="Lake Saiful Muluk",
        name_gojri="جھیل سیف الملوک",
        region="Kaghan Valley, Hazara",
        altitude_m=3224,
        historical_significance="High alpine glacial lake immortalized in Mian Muhammad Bakhsh's classical Gojri verse romance 'Saiful Malook'.",
    ),
]

_TRIBAL_CLANS: List[TribalClan] = [
    TribalClan(
        name="Khatana",
        name_gojri="کھٹانہ",
        historical_roots="One of the largest classical Gujjar clans, associated with ancient royal lineages and prominent transhumant leaders.",
        prominent_regions=["Jammu & Kashmir", "Punjab", "Khyber Pakhtunkhwa", "Himachal Pradesh"],
    ),
    TribalClan(
        name="Kasana",
        name_gojri="کسانہ",
        historical_roots="Ancient royal and pastoral clan traced historically to Kushan and Gurjara-Pratihara affiliations.",
        prominent_regions=["Jammu", "Poonch", "Rajasthan", "Haryana", "Western UP"],
    ),
    TribalClan(
        name="Chauhan",
        name_gojri="چوہان",
        historical_roots="Distinguished warrior-pastoral clan with extensive presence in Pir Panjal hills.",
        prominent_regions=["Rajouri", "Poonch", "Swat", "Hazara"],
    ),
    TribalClan(
        name="Bajar",
        name_gojri="بجڑ",
        historical_roots="Pastoral cattle-herding clan famous for buffalo husbandry in Chenab valley.",
        prominent_regions=["Reasi", "Rajouri", "Jammu"],
    ),
    TribalClan(
        name="Chechi",
        name_gojri="چیچی",
        historical_roots="Major ancestral clan celebrated in Gojri folk songs and pastoral narratives.",
        prominent_regions=["Kashmir", "Poonch", "Punjab Hills"],
    ),
    TribalClan(
        name="Poswal",
        name_gojri="پوسوال",
        historical_roots="Pastoral mountain clan residing along the Shivalik and Pir Panjal slopes.",
        prominent_regions=["Jammu", "Himachal Pradesh", "Poonch"],
    ),
]


def list_historical_places() -> List[HistoricalPlace]:
    """Return documented historical places and mountain passes."""
    return list(_HISTORICAL_PLACES)


def list_tribal_clans() -> List[TribalClan]:
    """Return documented Gujjar ancestral clans and lineages."""
    return list(_TRIBAL_CLANS)


def search_historical_knowledge(query: str) -> Dict[str, Any]:
    """Search historical places, transhumance geography, and tribal clans."""
    q_norm = normalize_for_search(query)
    places = [
        p.to_dict() for p in _HISTORICAL_PLACES
        if q_norm in normalize_for_search(p.name)
        or q_norm in normalize_for_search(p.name_gojri)
        or q_norm in normalize_for_search(p.region)
        or q_norm in normalize_for_search(p.historical_significance)
    ]
    clans = [
        c.to_dict() for c in _TRIBAL_CLANS
        if q_norm in normalize_for_search(c.name)
        or q_norm in normalize_for_search(c.name_gojri)
        or q_norm in normalize_for_search(c.historical_roots)
    ]
    return {
        "query": query,
        "places": places,
        "clans": clans,
        "total_matches": len(places) + len(clans),
    }
