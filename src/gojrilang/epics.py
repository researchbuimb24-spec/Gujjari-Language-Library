"""Epic literature management subsystem for Gojri language texts.

Provides structured access to classical and oral epic traditions of Gujari / Gojri,
specifically the Gojri Ramayana (Kandas, Chapters, Verses) and Gojri Mahabharata
(Parvas, Chapters, Verses), complete with verse-level multiscript text, translations,
vocabulary extraction, cultural notes, and audio narration metadata.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from gojrilang.exceptions import GojriLangError
from gojrilang.normalize import normalize_for_search


class EpicNotFoundError(GojriLangError):
    """Raised when an epic, kanda/parva, chapter, or verse is not found."""

    def __init__(self, identifier: str, details: Optional[str] = None) -> None:
        msg = f"Epic resource '{identifier}' was not found in the Gojri literature archive."
        if details:
            msg += f" Details: {details}"
        super().__init__(msg)
        self.identifier = identifier
        self.details = details


@dataclass
class EpicVerse:
    """A single verse or passage within an epic chapter."""

    verse_num: int
    text_perso_arabic: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None
    translation_en: str = ""
    translation_hi: Optional[str] = None
    translation_ur: Optional[str] = None
    vocabulary: List[Dict[str, str]] = field(default_factory=list)
    cultural_notes: Optional[str] = None
    audio_ref: Optional[str] = None
    alignment_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpicVerse:
        return cls(
            verse_num=int(data["verse_num"]),
            text_perso_arabic=data.get("text_perso_arabic", ""),
            text_devanagari=data.get("text_devanagari"),
            text_roman=data.get("text_roman"),
            translation_en=data.get("translation_en", ""),
            translation_hi=data.get("translation_hi"),
            translation_ur=data.get("translation_ur"),
            vocabulary=data.get("vocabulary", []),
            cultural_notes=data.get("cultural_notes"),
            audio_ref=data.get("audio_ref"),
            alignment_id=data.get("alignment_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_text(self, script: str = "perso-arabic") -> str:
        s_clean = script.lower().strip()
        if "perso" in s_clean or "arabic" in s_clean or "urdu" in s_clean:
            return self.text_perso_arabic
        if "devanagari" in s_clean or "hindi" in s_clean:
            return self.text_devanagari or self.text_perso_arabic
        if "roman" in s_clean or "latin" in s_clean:
            return self.text_roman or self.text_perso_arabic
        return self.text_perso_arabic


@dataclass
class EpicChapter:
    """A chapter within an epic Kanda or Parva."""

    chapter_num: int
    title: str
    title_gojri: str = ""
    summary: str = ""
    verses: List[EpicVerse] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpicChapter:
        return cls(
            chapter_num=int(data["chapter_num"]),
            title=data.get("title", ""),
            title_gojri=data.get("title_gojri", ""),
            summary=data.get("summary", ""),
            verses=[EpicVerse.from_dict(v) for v in data.get("verses", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_num": self.chapter_num,
            "title": self.title,
            "title_gojri": self.title_gojri,
            "summary": self.summary,
            "verses": [v.to_dict() for v in self.verses],
        }

    def get_verse(self, verse_num: int) -> EpicVerse:
        for v in self.verses:
            if v.verse_num == verse_num:
                return v
        raise EpicNotFoundError(f"Verse {verse_num}", f"in chapter '{self.title}'")

    def extract_vocabulary(self) -> List[Dict[str, str]]:
        all_vocab: List[Dict[str, str]] = []
        for v in self.verses:
            all_vocab.extend(v.vocabulary)
        return all_vocab


@dataclass
class EpicKandaParva:
    """A major section (Kanda for Ramayana, Parva for Mahabharata) of an epic."""

    id: str
    name: str = ""
    name_gojri: str = ""
    section_num: int = 1
    chapters: List[EpicChapter] = field(default_factory=list)
    title: str = ""

    def __post_init__(self) -> None:
        if self.title and not self.name:
            self.name = self.title
        elif self.name and not self.title:
            self.title = self.name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpicKandaParva:
        return cls(
            id=data["id"],
            name=data.get("name", data.get("title", "")),
            name_gojri=data.get("name_gojri", ""),
            section_num=int(data.get("section_num", 1)),
            chapters=[EpicChapter.from_dict(c) for c in data.get("chapters", [])],
            title=data.get("title", data.get("name", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "title": self.name,
            "name_gojri": self.name_gojri,
            "section_num": self.section_num,
            "chapters": [c.to_dict() for c in self.chapters],
        }

    def get_chapter(self, chapter_num: int) -> EpicChapter:
        for c in self.chapters:
            if c.chapter_num == chapter_num:
                return c
        raise EpicNotFoundError(f"Chapter {chapter_num}", f"in section '{self.name}'")


class Epic:
    """A complete epic work in the Gojri literature repository."""

    def __init__(
        self,
        id: str,
        title: str,
        title_gojri: str,
        tradition: str,
        structure_type: str = "section",
        description: str = "",
        sections: Optional[List[EpicKandaParva]] = None,
        source: str = "JKAACL Oral Traditions / Field Lore",
        license: str = "Archival Open Access",
    ) -> None:
        self.id = id
        self.title = title
        self.title_gojri = title_gojri
        self.tradition = tradition
        self.structure_type = structure_type
        self.description = description
        self.sections = sections or []
        self.source = source
        self.license = license
        self._section_map: Dict[str, EpicKandaParva] = {}
        for s in self.sections:
            self._section_map[s.id.lower()] = s
            self._section_map[str(s.section_num)] = s
            self._section_map[s.name.lower()] = s
            if s.title:
                self._section_map[s.title.lower()] = s

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Epic:
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            title_gojri=data.get("title_gojri", ""),
            tradition=data.get("tradition", "Himalayan Oral Lore"),
            structure_type=data.get("structure_type", "section"),
            description=data.get("description", ""),
            sections=[EpicKandaParva.from_dict(s) for s in data.get("sections", [])],
            source=data.get("source", "JKAACL Oral Traditions / Field Lore"),
            license=data.get("license", "Archival Open Access"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_gojri": self.title_gojri,
            "tradition": self.tradition,
            "structure_type": self.structure_type,
            "description": self.description,
            "source": self.source,
            "license": self.license,
            "sections": [s.to_dict() for s in self.sections],
        }

    def get_section(self, section: Union[str, int]) -> EpicKandaParva:
        s_key = str(section).strip().lower()
        if s_key in self._section_map:
            return self._section_map[s_key]
        for k, v in self._section_map.items():
            if s_key in k:
                return v
        raise EpicNotFoundError(f"Section '{section}'", f"in epic '{self.title}'")

    def get_chapter(self, section: Union[str, int], chapter_num: int) -> EpicChapter:
        sec = self.get_section(section)
        return sec.get_chapter(chapter_num)

    def get_verse(self, section: Union[str, int], chapter_num: int, verse_num: int) -> EpicVerse:
        chap = self.get_chapter(section, chapter_num)
        return chap.get_verse(verse_num)

    def extract_all_vocabulary(self) -> List[Dict[str, str]]:
        vocab: List[Dict[str, str]] = []
        for s in self.sections:
            for c in s.chapters:
                vocab.extend(c.extract_vocabulary())
        return vocab

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []
        q_norm = normalize_for_search(query)
        results: List[Dict[str, Any]] = []
        for s in self.sections:
            for c in s.chapters:
                for v in c.verses:
                    corpus = [
                        normalize_for_search(v.text_perso_arabic),
                        normalize_for_search(v.text_devanagari or ""),
                        normalize_for_search(v.text_roman or ""),
                        normalize_for_search(v.translation_en),
                        normalize_for_search(v.translation_hi or ""),
                        normalize_for_search(v.translation_ur or ""),
                        normalize_for_search(v.cultural_notes or ""),
                    ]
                    if any(q_norm in f for f in corpus if f):
                        results.append({
                            "epic_id": self.id,
                            "epic_title": self.title,
                            "section_id": s.id,
                            "section_name": s.name,
                            "chapter_num": c.chapter_num,
                            "chapter_title": c.title,
                            "verse_num": v.verse_num,
                            "verse": v.to_dict(),
                        })
        return results

    def __repr__(self) -> str:
        return f"<Epic id='{self.id}' title='{self.title}' sections={len(self.sections)}>"


_EPICS_REGISTRY: Optional[Dict[str, Epic]] = None


def _get_epics_registry() -> Dict[str, Epic]:
    global _EPICS_REGISTRY
    if _EPICS_REGISTRY is None:
        ref = resources.files("gojrilang.data").joinpath("epics.json")
        if ref.is_file():
            with ref.open("r", encoding="utf-8") as f:
                data = json.load(f)
            _EPICS_REGISTRY = {
                e["id"]: Epic.from_dict(e) for e in data.get("epics", [])
            }
        else:
            _EPICS_REGISTRY = {}
    return _EPICS_REGISTRY


def list_epics() -> List[Dict[str, Any]]:
    """List metadata for all documented Gojri epics."""
    reg = _get_epics_registry()
    results = []
    for e in reg.values():
        total_chapters = sum(len(s.chapters) for s in e.sections)
        total_verses = sum(sum(len(c.verses) for c in s.chapters) for s in e.sections)
        results.append({
            "id": e.id,
            "title": e.title,
            "title_gojri": e.title_gojri,
            "tradition": e.tradition,
            "structure_type": e.structure_type,
            "sections_count": len(e.sections),
            "total_sections": len(e.sections),
            "chapters_count": total_chapters,
            "total_chapters": total_chapters,
            "verses_count": total_verses,
            "total_verses": total_verses,
            "source": e.source,
            "license": e.license,
            "description": e.description,
        })
    return results


def get_epic(epic_id: str) -> Epic:
    """Retrieve an epic by its identifier (e.g. 'gojri_ramayana', 'gojri_mahabharata')."""
    reg = _get_epics_registry()
    clean_id = epic_id.strip().lower()
    if clean_id in reg:
        return reg[clean_id]
    for k, v in reg.items():
        if clean_id in k or clean_id in v.title.lower():
            return v
    raise EpicNotFoundError(epic_id)


def get_epic_chapter(
    epic_id: str,
    section_or_chapter: Union[str, int],
    chapter_num: Optional[int] = None,
) -> EpicChapter:
    """Retrieve a specific chapter from an epic."""
    epic = get_epic(epic_id)
    if chapter_num is None:
        chap = int(section_or_chapter)
        sec = epic.sections[0].id if epic.sections else 1
        return epic.get_chapter(sec, chap)
    else:
        return epic.get_chapter(section_or_chapter, chapter_num)


def get_epic_verse(
    epic_id: str,
    section_or_chapter: Union[str, int],
    chapter_or_verse: int,
    verse_num: Optional[int] = None,
) -> EpicVerse:
    """Retrieve a specific verse from an epic chapter."""
    epic = get_epic(epic_id)
    if verse_num is None:
        chap = int(section_or_chapter)
        v_num = chapter_or_verse
        sec = epic.sections[0].id if epic.sections else 1
        return epic.get_verse(sec, chap, v_num)
    else:
        return epic.get_verse(section_or_chapter, chapter_or_verse, verse_num)


def search_epics(query: str) -> List[Dict[str, Any]]:
    """Search for keywords, characters, or topics across all Gojri epics."""
    all_results = []
    for epic in _get_epics_registry().values():
        all_results.extend(epic.search(query))
    return all_results


def register_epic(epic_data: Union[Epic, Dict[str, Any]]) -> Epic:
    """Register a new or custom epic dataset in the active runtime registry."""
    if isinstance(epic_data, dict):
        epic_obj = Epic.from_dict(epic_data)
    elif isinstance(epic_data, Epic):
        epic_obj = epic_data
    else:
        raise TypeError(f"Expected Epic or dict, got {type(epic_data).__name__}")
    reg = _get_epics_registry()
    reg[epic_obj.id] = epic_obj
    return epic_obj


def reset_epics_registry() -> None:
    """Reset the cached epics registry."""
    global _EPICS_REGISTRY
    _EPICS_REGISTRY = None
