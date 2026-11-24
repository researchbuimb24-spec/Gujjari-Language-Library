"""Audio and speech infrastructure for native Gojri spoken archives.

Provides data models, metadata registries, speaker demographics, recording quality
specifications, and transcription alignment interfaces for:
- Lexical word pronunciations
- Sentence and dialogue recordings
- Traditional songs and ballads
- Story and epic narration
- Oral history interviews

Designed as an extensible metadata foundation for future speech-to-text (STT)
and text-to-speech (TTS) research without making unsubstantiated claims.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from gojrilang.exceptions import GojriLangError


class AudioResourceNotFoundError(GojriLangError):
    """Raised when an audio recording resource is not found."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(f"Audio recording '{resource_id}' was not found in the speech archive.")
        self.resource_id = resource_id


@dataclass
class SpeakerDemographics:
    """Metadata describing a native speaker contributor."""

    speaker_id: str
    dialect_region: str
    gender: str = "unspecified"
    age_group: str = "adult"  # youth, adult, elder
    native_speaker: bool = True
    home_village_or_town: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudioQuality:
    """Technical quality parameters for an archival recording."""

    sample_rate_hz: int = 44100
    channels: int = 1  # 1 = mono, 2 = stereo
    format: str = "flac"  # flac, wav, mp3, ogg
    duration_seconds: float = 0.0
    bitrate_kbps: Optional[int] = 128
    snr_db: Optional[float] = None  # Signal-to-Noise Ratio estimation

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecordingPermission:
    """Legal rights, licensing, and consent parameters for language documentation."""

    license_type: str = "CC-BY-NC-SA-4.0"
    attribution_required: bool = True
    commercial_allowed: bool = False
    consent_recorded: bool = True
    contributor_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudioRecording:
    """A documented spoken audio record with metadata and transcription alignment."""

    id: str
    resource_type: str  # word, sentence, song, narration, oral_history
    resource_id: str  # Associated dictionary entry id, sentence id, song id, etc.
    audio_url: str
    transcript_gojri: str
    transcript_roman: Optional[str] = None
    speaker: SpeakerDemographics = field(default_factory=lambda: SpeakerDemographics("anon", "Pir Panjal"))
    quality: AudioQuality = field(default_factory=AudioQuality)
    permission: RecordingPermission = field(default_factory=RecordingPermission)
    alignment_timestamps: List[Dict[str, Any]] = field(default_factory=list)
    verification_status: str = "verified"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "audio_url": self.audio_url,
            "transcript_gojri": self.transcript_gojri,
            "transcript_roman": self.transcript_roman,
            "speaker": self.speaker.to_dict(),
            "quality": self.quality.to_dict(),
            "permission": self.permission.to_dict(),
            "alignment_timestamps": self.alignment_timestamps,
            "verification_status": self.verification_status,
        }


_AUDIO_ARCHIVE: Dict[str, AudioRecording] = {
    "rec_word_ghoro": AudioRecording(
        id="rec_word_ghoro",
        resource_type="word",
        resource_id="word_001",
        audio_url="https://archive.org/download/gojrilang-corpus/audio/words/word_001_ghoro.wav",
        transcript_gojri="گھوڑو",
        transcript_roman="ghoṛo",
        speaker=SpeakerDemographics(
            speaker_id="SPK_JK_POONCH_01",
            dialect_region="Poonch, J&K",
            gender="male",
            age_group="elder",
            native_speaker=True,
            home_village_or_town="Surankote",
        ),
        quality=AudioQuality(sample_rate_hz=48000, channels=1, format="wav", duration_seconds=1.2),
        permission=RecordingPermission(license_type="CC-BY-NC-4.0", consent_recorded=True),
        alignment_timestamps=[{"start_ms": 100, "end_ms": 1100, "text": "ghoṛo"}],
    ),
    "rec_song_chhaint": AudioRecording(
        id="rec_song_chhaint",
        resource_type="song",
        resource_id="SONG_CHHAINT_01",
        audio_url="https://archive.org/download/gojrilang-corpus/audio/songs/chhaint_pir_panjal.mp3",
        transcript_gojri="پیر پنجال دیاں اُچیاں دھاراں",
        transcript_roman="Pīr Panjāl diyā̃ uchīyā̃ dhārā̃",
        speaker=SpeakerDemographics(
            speaker_id="SPK_DADHI_01",
            dialect_region="Pir Panjal",
            gender="male",
            age_group="elder",
            native_speaker=True,
        ),
        quality=AudioQuality(sample_rate_hz=44100, channels=2, format="mp3", duration_seconds=185.0),
        permission=RecordingPermission(license_type="CC-BY-NC-SA-4.0", consent_recorded=True),
    ),
}


def get_audio_recording(recording_id: str) -> Optional[AudioRecording]:
    """Retrieve an audio recording by its ID."""
    return _AUDIO_ARCHIVE.get(recording_id.strip())


def list_audio_recordings(
    resource_type: Optional[str] = None,
    dialect_region: Optional[str] = None,
) -> List[AudioRecording]:
    """List audio recordings filtered by resource type or speaker dialect region."""
    results = []
    for rec in _AUDIO_ARCHIVE.values():
        if resource_type and rec.resource_type.lower() != resource_type.strip().lower():
            continue
        if dialect_region and dialect_region.strip().lower() not in rec.speaker.dialect_region.lower():
            continue
        results.append(rec)
    return results


def register_audio_recording(recording: Union[AudioRecording, Dict[str, Any]]) -> AudioRecording:
    """Register a new audio recording entry into the speech archive."""
    if isinstance(recording, dict):
        rec_obj = AudioRecording(
            id=recording["id"],
            resource_type=recording.get("resource_type", "word"),
            resource_id=recording.get("resource_id", ""),
            audio_url=recording.get("audio_url", ""),
            transcript_gojri=recording.get("transcript_gojri", ""),
            transcript_roman=recording.get("transcript_roman"),
            speaker=SpeakerDemographics(**recording.get("speaker", {"speaker_id": "anon", "dialect_region": "General"})),
            quality=AudioQuality(**recording.get("quality", {})),
            permission=RecordingPermission(**recording.get("permission", {})),
            alignment_timestamps=recording.get("alignment_timestamps", []),
            verification_status=recording.get("verification_status", "verified"),
        )
    elif isinstance(recording, AudioRecording):
        rec_obj = recording
    else:
        raise TypeError(f"Expected AudioRecording or dict, got {type(recording).__name__}")
    _AUDIO_ARCHIVE[rec_obj.id] = rec_obj
    return rec_obj
