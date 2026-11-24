"""Community contributor registry and attribution subsystem for GojriLang."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.exceptions import GojriLangError


class ContributorNotFoundError(GojriLangError):
    """Raised when a contributor ID is not found."""

    def __init__(self, contributor_id: str) -> None:
        super().__init__(f"Contributor '{contributor_id}' was not found.")
        self.contributor_id = contributor_id


@dataclass
class Contributor:
    """A documented community contributor, linguist, or authorized reviewer."""

    id: str
    name: str
    role: str  # contributor, native_speaker_consultant, reviewer, linguist, administrator
    affiliation: Optional[str] = None
    email_or_contact: Optional[str] = None
    dialect_expertise: List[str] = None  # type: ignore[assignment]
    joined_year: int = 2026
    contributions_count: int = 0

    def __post_init__(self) -> None:
        if self.dialect_expertise is None:
            self.dialect_expertise = ["General Gojri"]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_CONTRIBUTORS_REGISTRY: Dict[str, Contributor] = {
    "CONTRIB_JKAACL_01": Contributor(
        id="CONTRIB_JKAACL_01",
        name="JKAACL Gojri Section Documentation Team",
        role="reviewer",
        affiliation="Jammu & Kashmir Academy of Art, Culture and Languages",
        dialect_expertise=["Poonchi", "Pir Panjal", "Jammu"],
        contributions_count=225,
    ),
    "CONTRIB_CIIL_01": Contributor(
        id="CONTRIB_CIIL_01",
        name="CIIL Mysore Linguistic Fieldwork Team (J. C. Sharma)",
        role="linguist",
        affiliation="Central Institute of Indian Languages, Mysore",
        dialect_expertise=["General Gojri"],
        contributions_count=50,
    ),
    "CONTRIB_SIL_01": Contributor(
        id="CONTRIB_SIL_01",
        name="SIL International Literacy Research (Wayne E. Losey)",
        role="linguist",
        affiliation="SIL International",
        dialect_expertise=["Western Hazara", "Northern Gojri"],
        contributions_count=35,
    ),
    "CONTRIB_COMMUNITY_01": Contributor(
        id="CONTRIB_COMMUNITY_01",
        name="Pir Panjal Gujjar & Bakarwal Youth Cultural Forum",
        role="contributor",
        affiliation="Poonch-Rajouri Cultural Heritage Circle",
        dialect_expertise=["Poonchi", "Rajouri"],
        contributions_count=15,
    ),
}


def list_contributors(role: Optional[str] = None) -> List[Contributor]:
    """List all registered contributors, optionally filtered by role."""
    results = []
    for c in _CONTRIBUTORS_REGISTRY.values():
        if role and c.role.lower() != role.strip().lower():
            continue
        results.append(c)
    return results


def get_contributor(contributor_id: str) -> Contributor:
    """Retrieve a contributor record by ID."""
    clean_id = contributor_id.strip()
    if clean_id in _CONTRIBUTORS_REGISTRY:
        return _CONTRIBUTORS_REGISTRY[clean_id]
    raise ContributorNotFoundError(contributor_id)


def register_contributor(
    id_or_contributor: Union[str, Contributor],
    name: Optional[str] = None,
    role: str = "contributor",
    affiliation: Optional[str] = None,
    dialect_expertise: Optional[List[str]] = None,
) -> Contributor:
    """Register a new community contributor or reviewer."""
    if isinstance(id_or_contributor, Contributor):
        c = id_or_contributor
    else:
        c = Contributor(
            id=str(id_or_contributor).strip(),
            name=(name or str(id_or_contributor)).strip(),
            role=role.strip().lower(),
            affiliation=affiliation,
            dialect_expertise=dialect_expertise or ["General Gojri"],
        )
    _CONTRIBUTORS_REGISTRY[c.id] = c
    return c
