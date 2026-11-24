"""Tests for Gojri traditional songs, musicological metadata, and lyrics subsystem."""

import pytest
from gojrilang.exceptions import GojriLangError
from gojrilang.lyrics import format_multiscript_lyrics, search_lyrics
from gojrilang.songs import (
    SongNotFoundError,
    SongRecord,
    get_song,
    get_song_lyrics,
    list_song_categories,
    list_songs,
    search_songs,
)


def test_list_songs():
    songs = list_songs()
    assert len(songs) >= 7
    song_ids = {s.id for s in songs}
    assert "SONG_CHHAINT_01" in song_ids
    assert "SONG_MAHYA_01" in song_ids
    assert "SONG_LORI_01" in song_ids


def test_list_song_categories():
    categories = list_song_categories()
    assert "chhaint" in categories
    assert "mahya" in categories
    assert "lori" in categories
    assert "bait" in categories
    assert len(categories) >= 4


def test_list_songs_category_filter():
    lori_songs = list_songs(category="lori")
    assert len(lori_songs) >= 1
    assert all(s.category == "lori" for s in lori_songs)

    chhaint_songs = list_songs(category="chhaint")
    assert len(chhaint_songs) >= 1
    assert all(s.category == "chhaint" for s in chhaint_songs)


def test_get_song():
    song = get_song("SONG_CHHAINT_01")
    assert isinstance(song, SongRecord)
    assert song.id == "SONG_CHHAINT_01"
    assert "Chhaint" in song.title
    assert song.category == "chhaint"
    assert len(song.verses) >= 1
    assert len(song.musical_instruments) >= 1
    assert "alghoza" in song.musical_instruments or "bansuri" in song.musical_instruments


def test_get_song_not_found_raises():
    with pytest.raises(SongNotFoundError):
        get_song("NONEXISTENT_SONG_999")


def test_get_song_lyrics():
    lyrics_pa = get_song_lyrics("SONG_CHHAINT_01", script="perso-arabic")
    assert len(lyrics_pa) >= 1
    assert any("پیر پنجال" in line or "دھاراں" in line or "گوجر" in line for line in lyrics_pa)

    lyrics_dev = get_song_lyrics("SONG_CHHAINT_01", script="devanagari")
    assert len(lyrics_dev) >= 1

    lyrics_rom = get_song_lyrics("SONG_CHHAINT_01", script="roman")
    assert len(lyrics_rom) >= 1


def test_search_songs():
    results = search_songs("lullaby")
    assert len(results) >= 1
    assert any(s.category == "lori" for s in results)

    results_pa = search_songs("پنجال")
    assert len(results_pa) >= 1


def test_format_multiscript_lyrics():
    song = get_song("SONG_MAHYA_01")
    aligned = format_multiscript_lyrics(song)
    assert len(aligned) == len(song.verses)
    assert "perso_arabic" in aligned[0]
    assert "devanagari" in aligned[0]
    assert "roman" in aligned[0]
    assert "translation_en" in aligned[0]


def test_search_lyrics():
    matches = search_lyrics("lullaby")
    assert len(matches) >= 1
    assert any(m["category"] == "lori" for m in matches)
