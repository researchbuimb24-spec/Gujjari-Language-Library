"""Dialect and regional variation engine for Gojri.

Provides documented profiles for regional varieties across Jammu & Kashmir,
Himachal Pradesh, Khyber Pakhtunkhwa (Hazara/Swat), and the Rajasthani border.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from importlib import resources
from typing import Any, Dict, List, Optional

from gojrilang.dictionary import lookup
from gojrilang.exceptions import DialectProfileNotFoundError


@dataclass
class DialectProfile:
    """Documented linguistic profile of a regional Gojri variety."""

    id: str
    name: str
    region: str
    script_preference: str
    phonology: Dict[str, Any]
    grammar: Dict[str, str]
    vocabulary_variants: Dict[str, str]
    confidence: str
    sources: List[str]

    @property
    def phonological_features(self) -> List[str]:
        features = self.phonology.get("key_features", [])
        if isinstance(features, list) and features:
            return features
        return [f"{k}: {v}" for k, v in self.phonology.items()]

    @property
    def lexical_variants(self) -> Dict[str, str]:
        return self.vocabulary_variants

    @property
    def references(self) -> List[str]:
        return self.sources

    @property
    def sub_dialects(self) -> List[str]:
        sub = self.region.split("(")[-1].replace(")", "") if "(" in self.region else self.region
        return [s.strip() for s in sub.split(",") if s.strip()]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DialectProfile:
        return cls(
            id=data["id"],
            name=data["name"],
            region=data["region"],
            script_preference=data.get("script_preference", "Extended Perso-Arabic"),
            phonology=data.get("phonology", {}),
            grammar=data.get("grammar", {}),
            vocabulary_variants=data.get("vocabulary_variants", {}),
            confidence=data.get("confidence", "provisional"),
            sources=data.get("sources", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} ({self.region}) [{self.confidence}]"


_DIALECT_CACHE: Optional[Dict[str, DialectProfile]] = None


def _load_dialect_profiles() -> Dict[str, DialectProfile]:
    global _DIALECT_CACHE
    if _DIALECT_CACHE is not None:
        return _DIALECT_CACHE

    ref = resources.files("gojrilang.data").joinpath("dialects.json")
    with ref.open("r", encoding="utf-8") as f:
        data = json.load(f)

    _DIALECT_CACHE = {
        p["id"]: DialectProfile.from_dict(p) for p in data.get("profiles", [])
    }
    return _DIALECT_CACHE


def list_dialect_profiles() -> List[DialectProfile]:
    """Return all documented Gojri regional dialect profiles."""
    return list(_load_dialect_profiles().values())


def get_dialect_profile(profile_id: str) -> DialectProfile:
    """Retrieve a dialect profile by ID (e.g. 'jk_poonchi', 'western_hazara').

    Args:
        profile_id: Unique profile identifier.

    Returns:
        DialectProfile instance.

    Raises:
        DialectProfileNotFoundError: If profile_id is not documented.
    """
    profiles = _load_dialect_profiles()
    clean_id = profile_id.strip().lower()
    res = profiles.get(clean_id)
    if not res:
        raise DialectProfileNotFoundError(profile_id)
    return res


def compare_variants(
    word: str,
    profiles: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Compare a Gojri word across documented regional dialect profiles.

    Args:
        word: Gojri word (e.g. 'ghoṛo', 'گھوڑو', 'ro', 'رو').
        profiles: Optional list of dialect profile IDs to restrict comparison.

    Returns:
        Dictionary mapping profile IDs to attested forms and grammatical traits.
    """
    all_profiles = _load_dialect_profiles()
    target_profiles = [all_profiles[p] for p in profiles if p in all_profiles] if profiles else list(all_profiles.values())

    results: Dict[str, Any] = {
        "word": word,
        "comparisons": {},
        "notes": "Dialect comparisons are derived from published surveys (Sharma 1982, Losey 2002, Grierson LSI).",
    }

    clean = word.strip().lower()
    entry = lookup(word)

    for p in target_profiles:
        profile_data: Dict[str, Any] = {
            "name": p.name,
            "region": p.region,
            "script": p.script_preference,
            "attested_form": None,
            "genitive_marker": p.grammar.get("genitive_marker"),
            "masculine_noun_ending": p.grammar.get("masculine_noun_ending"),
        }

        # Check vocabulary variants in profile
        for concept, variant in p.vocabulary_variants.items():
            if clean in variant.lower() or (entry and entry.meaning_en.lower() in concept):
                profile_data["attested_form"] = variant
                break

        # Fallback to general morphological prediction based on dialect profile
        if profile_data["attested_form"] is None:
            if p.id == "western_hazara" and clean.endswith("و"):
                profile_data["predicted_western_form"] = clean[:-1] + "ا (in -ā)"
            elif p.id == "western_hazara" and clean.endswith("o"):
                profile_data["predicted_western_form"] = clean[:-1] + "ā (in -ā)"
            elif p.id == "jk_poonchi" and clean.endswith("ا"):
                profile_data["predicted_poonchi_form"] = clean[:-1] + "و (in -o)"

        results["comparisons"][p.id] = profile_data

    return results
