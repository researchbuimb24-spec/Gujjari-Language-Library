"""Gojri lyric processing, alignment, and formatting utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from gojrilang.normalize import normalize_for_search
from gojrilang.songs import SongRecord, list_songs


def search_lyrics(query: str, script: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for lyrical phrases or keywords across all documented song verses."""
    if not query or not query.strip():
        return []
    q_norm = normalize_for_search(query)
    matches = []
    for song in list_songs():
        for verse in song.verses:
            target_text = verse.get_text(script) if script else (
                f"{song.title} {song.category} {verse.text_perso_arabic} {verse.text_devanagari or ''} "
                f"{verse.text_roman or ''} {verse.translation_en}"
            )
            if q_norm in normalize_for_search(target_text):
                matches.append({
                    "song_id": song.id,
                    "song_title": song.title,
                    "category": song.category,
                    "verse_num": verse.verse_num,
                    "text": verse.get_text(script or "perso-arabic"),
                    "translation_en": verse.translation_en,
                })
    return matches


def format_multiscript_lyrics(song: SongRecord) -> List[Dict[str, Any]]:
    """Format lyrics of a song aligning Perso-Arabic, Devanagari, Roman, and English."""
    aligned = []
    for v in song.verses:
        aligned.append({
            "verse_num": v.verse_num,
            "perso_arabic": v.text_perso_arabic,
            "devanagari": v.text_devanagari,
            "roman": v.text_roman,
            "translation_en": v.translation_en,
        })
    return aligned
