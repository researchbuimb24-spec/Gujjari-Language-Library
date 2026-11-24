"""GojriLang: Digital Language, Literature, Cultural Heritage & AI Infrastructure for Gujari / Gojri.

Gojri (ISO 639-3: gju) is an Indo-Aryan language spoken across Jammu & Kashmir,
Himachal Pradesh, Punjab, Rajasthan, and adjacent northwestern regions.

Project vision:
GojriLang — Preserving Words. Protecting Heritage. Connecting Generations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

# Subsystem Imports
from gojrilang.audio import (
    AudioQuality,
    AudioRecording,
    AudioResourceNotFoundError,
    RecordingPermission,
    SpeakerDemographics,
    get_audio_recording,
    list_audio_recordings,
    register_audio_recording,
)
from gojrilang.books import (
    Book,
    BookMetadata,
    BookPage,
    BookSearchResult,
    get_book,
    get_page,
    import_book_file,
    list_books,
    register_book,
    reset_registry,
    search_books,
)
from gojrilang.contributors import (
    Contributor,
    ContributorNotFoundError,
    get_contributor,
    list_contributors,
    register_contributor,
)
from gojrilang.corpus import (
    Corpus,
    CorpusStatistics,
    concordance,
    get_corpus,
    get_corpus_statistics,
)
from gojrilang.culture import (
    CulturalItem,
    get_cultural_item,
    list_cultural_categories,
    list_items,
    list_proverbs,
    list_songs as list_cultural_songs,
    search_culture,
)
from gojrilang.datasets import (
    ImportReport,
    ValidationReport,
    export_file,
    get_dataset_stats,
    import_file,
    validate,
)
from gojrilang.dialects import (
    DialectProfile,
    compare_variants,
    get_dialect_profile,
    list_dialect_profiles,
)
from gojrilang.dictionary import (
    DictionaryEntry,
    ExampleSentence,
    find_synonyms,
    get_word_details,
    get_word_variants,
    lookup,
    lookup_all,
    search,
)
from gojrilang.epics import (
    Epic,
    EpicChapter,
    EpicKandaParva,
    EpicNotFoundError,
    EpicVerse,
    get_epic,
    get_epic_chapter,
    get_epic_verse,
    list_epics,
    register_epic,
    reset_epics_registry,
    search_epics,
)
from gojrilang.exceptions import (
    BookNotFoundError,
    DataSchemaValidationError,
    DatasetValidationError,
    DialectProfileNotFoundError,
    GojriLangError,
    InvalidDialectError,
    RuleNotFoundError,
    UnsupportedNumberRangeError,
    UnsupportedScriptError,
    UnsupportedTransliterationError,
    WordNotFoundError,
)
from gojrilang.folk_stories import (
    FolkStory,
    FolkStorySection,
    StoryNotFoundError,
    get_story,
    list_stories,
    search_stories,
)
from gojrilang.folklore import (
    PastoralCustom,
    Riddle,
    get_riddle,
    list_customs,
    list_riddles,
    search_folklore,
)
from gojrilang.grammar import (
    GrammarEngine,
    GrammarRule,
    explain_rule,
    get_grammar_engine,
    grammar_rules,
)
from gojrilang.historical_knowledge import (
    HistoricalPlace,
    TribalClan,
    list_historical_places,
    list_tribal_clans,
    search_historical_knowledge,
)
from gojrilang.literature import (
    LiteratureOverview,
    get_literature_overview,
    search_all_literature,
)
from gojrilang.lyrics import (
    format_multiscript_lyrics,
    search_lyrics,
)
from gojrilang.morphology import (
    WordAnalysis,
    analyze_word,
    generate_forms,
    lemmatize,
    list_documented_affixes,
)
from gojrilang.nlp import (
    detect_language,
    get_ngrams,
    pos_tag,
    sent_tokenize,
    spell_check,
    stem,
    text_similarity,
    tokenize,
)
from gojrilang.normalize import (
    UnicodeNormalizationForm,
    detect_script,
    normalize,
    normalize_for_search,
    normalize_spelling,
    strip_diacritics,
)
from gojrilang.numbers import (
    ordinal_to_words,
    parse_words,
    to_words,
)
from gojrilang.poetry import (
    Poem,
    PoemNotFoundError,
    PoemVerse,
    get_poem,
    list_poetic_forms,
    list_poems,
    search_poetry,
)
from gojrilang.pronunciation import (
    AudioReference,
    PhoneticInfo,
    get_audio,
    get_phonetics,
)
from gojrilang.proverbs import (
    get_proverb,
    search_proverbs,
)
from gojrilang.scripts import (
    get_supported_script_pairs,
    get_supported_scripts,
    is_rtl,
)
from gojrilang.search import (
    universal_search,
)
from gojrilang.songs import (
    SongLyricVerse,
    SongNotFoundError,
    SongRecord,
    get_song,
    get_song_lyrics,
    list_song_categories,
    list_songs,
    search_songs,
)
from gojrilang.storage import (
    GojriLexiconDB,
)
from gojrilang.translation import (
    TranslationResult,
    translate,
)
from gojrilang.transliteration import (
    romanize,
    supported_transliteration_pairs,
    transliterate,
)
from gojrilang.verification import (
    AuditLogEntry,
    Submission,
    VerificationWorkflowError,
    get_audit_history,
    get_submission,
    list_submissions,
    review_submission,
    submit_entry,
)
from gojrilang.vocabulary import (
    classify_word,
    get_vocabulary_summary,
    list_headwords,
)

__version__ = "0.3.0"

# Ensure search refers to dictionary.search rather than submodule
import gojrilang.dictionary as _dict_mod
search = _dict_mod.search


# ---------------------------------------------------------------------------
# Unified Gojri Object-Oriented Facade
# ---------------------------------------------------------------------------

class _DictionaryNamespace:
    """Namespace for dictionary lookup, gloss search, and synonyms."""

    def lookup(self, word: str, dialect: Optional[str] = None) -> Optional[DictionaryEntry]:
        return lookup(word, dialect=dialect)

    def lookup_all(self, word: str) -> List[DictionaryEntry]:
        return lookup_all(word)

    def search(
        self,
        query: str,
        language: str = "all",
        pos: Optional[str] = None,
        dialect: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[DictionaryEntry]:
        return _dict_mod.search(query, language=language, pos=pos, dialect=dialect, limit=limit)

    def translate(self, word: str, target: str = "english", source: str = "gojri") -> TranslationResult:
        return translate(word, source=source, target=target)

    def find_synonyms(self, word: str) -> List[str]:
        return find_synonyms(word)

    def get_word_details(self, entry_id: str) -> Optional[Dict[str, Any]]:
        return get_word_details(entry_id)

    def get_word_variants(self, word: str) -> Dict[str, Any]:
        return get_word_variants(word)


class _GrammarNamespace:
    """Namespace for grammar analysis, rules, and verb conjugation."""

    def analyze(self, sentence: str) -> Dict[str, Any]:
        engine = get_grammar_engine()
        return engine.analyze_sentence(sentence)

    def conjugate(
        self,
        verb_root: str,
        tense: Optional[str] = None,
        dialect: str = "general",
    ) -> Union[str, Dict[str, str]]:
        forms = generate_forms(verb_root, category="regular_verb", dialect=dialect)
        if tense:
            tense_clean = tense.strip().lower()
            if "past" in tense_clean:
                return forms.get("past_participle_masc_sg", forms.get("infinitive", ""))
            elif "present" in tense_clean:
                return forms.get("present_habitual_masc_sg", forms.get("infinitive", ""))
            elif "future" in tense_clean:
                return forms.get("future_masc_sg", forms.get("infinitive", ""))
            elif "imperative" in tense_clean:
                return forms.get("imperative_singular", forms.get("infinitive", ""))
        return forms

    def list_rules(self, category: Optional[str] = None, status: Optional[str] = None) -> List[GrammarRule]:
        return grammar_rules(category=category, status=status)

    def get_rule(self, rule_id: str) -> GrammarRule:
        engine = get_grammar_engine()
        return engine.get_rule(rule_id)

    def explain(self, rule_id: str) -> str:
        return explain_rule(rule_id)


class _ScriptsNamespace:
    """Namespace for script conversion, transliteration, normalization, and detection."""

    def transliterate(
        self,
        text: str,
        source: Optional[str] = None,
        target: str = "roman",
        source_script: Optional[str] = None,
        target_script: Optional[str] = None,
    ) -> str:
        src = source_script or source
        tgt = target_script or target
        return transliterate(text, source=src, target=tgt)

    def romanize(self, text: str, scheme: str = "academic") -> str:
        return romanize(text, scheme=scheme)

    def normalize(self, text: str, form: UnicodeNormalizationForm = "NFC") -> str:
        return normalize(text, normalize_unicode=form)

    def detect(self, text: str) -> str:
        return detect_script(text)

    def strip_diacritics(self, text: str) -> str:
        return strip_diacritics(text)

    def is_rtl(self, text: str) -> bool:
        return is_rtl(text)


class _DialectsNamespace:
    """Namespace for regional dialect profiling and variant comparison."""

    def list_profiles(self) -> List[DialectProfile]:
        return list_dialect_profiles()

    def get_profile(self, profile_id: str) -> DialectProfile:
        return get_dialect_profile(profile_id)

    def compare(self, word: str, profiles: Optional[List[str]] = None) -> Dict[str, Any]:
        return compare_variants(word, profiles=profiles)


class _LiteratureNamespace:
    """Namespace for literature books and historical corpus texts."""

    def list(self, category: Optional[str] = None) -> List[BookMetadata]:
        return list_books(category=category)

    def get_book(self, book_id: str) -> Book:
        return get_book(book_id)

    def get_page(self, book_id: str, page_number: int) -> BookPage:
        return get_page(book_id, page_number)

    def search(self, query: str) -> List[BookSearchResult]:
        return search_books(query)

    def overview(self) -> LiteratureOverview:
        return get_literature_overview()


class _EpicsNamespace:
    """Namespace for epic literature (Ramayana, Mahabharata)."""

    def list_epics(self) -> List[Dict[str, Any]]:
        return list_epics()

    def get_epic(self, epic_id: str) -> Epic:
        return get_epic(epic_id)

    def get_chapter(self, book: str, chapter: int, section: Optional[Union[str, int]] = None) -> EpicChapter:
        clean_book = book.strip().lower()
        epic_id = "gojri_ramayana" if "ram" in clean_book else ("gojri_mahabharata" if "maha" in clean_book or "pandav" in clean_book else clean_book)
        epic = get_epic(epic_id)
        sec = section or (epic.sections[0].id if epic.sections else 1)
        return epic.get_chapter(sec, chapter)

    def get_verse(self, book: str, chapter: int, verse: int, section: Optional[Union[str, int]] = None) -> EpicVerse:
        clean_book = book.strip().lower()
        epic_id = "gojri_ramayana" if "ram" in clean_book else ("gojri_mahabharata" if "maha" in clean_book or "pandav" in clean_book else clean_book)
        epic = get_epic(epic_id)
        sec = section or (epic.sections[0].id if epic.sections else 1)
        return epic.get_verse(sec, chapter, verse)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return search_epics(query)


class _SongsNamespace:
    """Namespace for traditional Gojri music and song archive."""

    def list(self, category: Optional[str] = None, dialect: Optional[str] = None) -> List[SongRecord]:
        return list_songs(category=category, dialect=dialect)

    def get(self, song_id: str) -> SongRecord:
        return get_song(song_id)

    def search(self, query: str, category: Optional[str] = None) -> List[SongRecord]:
        return search_songs(query, category=category)

    def categories(self) -> List[str]:
        return list_song_categories()

    def lyrics(self, song_id: str, script: str = "perso-arabic") -> List[str]:
        return get_song_lyrics(song_id, script=script)


class _FolkloreNamespace:
    """Namespace for proverbs, riddles, customs, and oral traditions."""

    def search(self, query: str) -> Dict[str, Any]:
        return search_folklore(query)

    def list_proverbs(self, dialect: Optional[str] = None) -> List[CulturalItem]:
        return list_proverbs(dialect=dialect)

    def get_proverb(self, proverb_id: str) -> Optional[CulturalItem]:
        return get_proverb(proverb_id)

    def list_riddles(self) -> List[Riddle]:
        return list_riddles()

    def list_customs(self, category: Optional[str] = None) -> List[PastoralCustom]:
        return list_customs(category=category)


class _CorpusNamespace:
    """Namespace for corpus analytics and concordances."""

    def statistics(self) -> CorpusStatistics:
        return get_corpus_statistics()

    def concordance(self, word: str, window: int = 4) -> List[Dict[str, Any]]:
        return concordance(word, window=window)

    def get_corpus(self) -> Corpus:
        return get_corpus()


class _NLPNamespace:
    """Namespace for computational linguistic tools."""

    def tokenize(self, text: str, preserve_punctuation: bool = True) -> List[str]:
        return tokenize(text, preserve_punctuation=preserve_punctuation)

    def sent_tokenize(self, text: str) -> List[str]:
        return sent_tokenize(text)

    def pos_tag(self, tokens_or_text: Union[str, List[str]]) -> List[Tuple[str, str]]:
        return pos_tag(tokens_or_text)

    def get_ngrams(self, tokens_or_text: Union[str, List[str]], n: int = 2) -> List[Tuple[str, ...]]:
        return get_ngrams(tokens_or_text, n=n)

    def spell_check(self, word: str, max_suggestions: int = 5) -> Dict[str, Any]:
        return spell_check(word, max_suggestions=max_suggestions)

    def similarity(self, text1: str, text2: str, method: str = "jaccard") -> float:
        return text_similarity(text1, text2, method=method)

    def detect_language(self, text: str) -> Dict[str, Any]:
        return detect_language(text)

    def stem(self, word: str) -> str:
        return stem(word)


class _AudioNamespace:
    """Namespace for spoken audio archives and metadata."""

    def get_recording(self, recording_id: str) -> Optional[AudioRecording]:
        return get_audio_recording(recording_id)

    def list_recordings(self, resource_type: Optional[str] = None, dialect_region: Optional[str] = None) -> List[AudioRecording]:
        return list_audio_recordings(resource_type=resource_type, dialect_region=dialect_region)

    def register_recording(self, recording: Union[AudioRecording, Dict[str, Any]]) -> AudioRecording:
        return register_audio_recording(recording)


class _VerificationNamespace:
    """Namespace for contributor verification and review workflows."""

    def submit(self, item_type: str, data: Dict[str, Any], contributor_id: str, source_citation: str) -> Submission:
        return submit_entry(item_type, data, contributor_id, source_citation)

    def review(self, submission_id: str, reviewer_id: str, new_status: str, comments: Optional[str] = None) -> Submission:
        return review_submission(submission_id, reviewer_id, new_status, comments=comments)

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        return get_submission(submission_id)

    def list_submissions(self, status: Optional[str] = None, item_type: Optional[str] = None) -> List[Submission]:
        return list_submissions(status=status, item_type=item_type)

    def audit_history(self, submission_id: Optional[str] = None) -> List[AuditLogEntry]:
        return get_audit_history(submission_id=submission_id)


class _VocabularyNamespace:
    """Namespace for lexical tier exploration and word classification."""

    def summary(self) -> Dict[str, Any]:
        return get_vocabulary_summary()

    def headwords(self, pos: Optional[str] = None, dialect: Optional[str] = None) -> List[str]:
        return list_headwords(pos=pos, dialect=dialect)

    def classify(self, word: str) -> Dict[str, Any]:
        return classify_word(word)


class Gojri:
    """Unified object-oriented facade providing direct access to all GojriLang subsystems.

    Example:
        >>> from gojrilang import Gojri
        >>> gju = Gojri()
        >>> entry = gju.dictionary.lookup("گھوڑو")
        >>> gju.scripts.transliterate("گھوڑو", target="devanagari")
        >>> gju.epics.get_chapter(book="ramayana", chapter=1)
        >>> gju.corpus.statistics()
    """

    def __init__(self) -> None:
        self.dictionary = _DictionaryNamespace()
        self.grammar = _GrammarNamespace()
        self.scripts = _ScriptsNamespace()
        self.dialects = _DialectsNamespace()
        self.literature = _LiteratureNamespace()
        self.epics = _EpicsNamespace()
        self.songs = _SongsNamespace()
        self.folklore = _FolkloreNamespace()
        self.corpus = _CorpusNamespace()
        self.nlp = _NLPNamespace()
        self.audio = _AudioNamespace()
        self.verification = _VerificationNamespace()
        self.vocabulary = _VocabularyNamespace()


__all__ = [
    "__version__",
    "Gojri",
    # Storage & DB
    "GojriLexiconDB",
    # Dictionary & Vocabulary
    "lookup",
    "lookup_all",
    "search",
    "find_synonyms",
    "get_word_details",
    "get_word_variants",
    "DictionaryEntry",
    "ExampleSentence",
    "get_vocabulary_summary",
    "list_headwords",
    "classify_word",
    # Text processing & Normalization
    "normalize",
    "normalize_spelling",
    "detect_script",
    "strip_diacritics",
    "normalize_for_search",
    "UnicodeNormalizationForm",
    # Transliteration & Romanization & Scripts
    "transliterate",
    "romanize",
    "supported_transliteration_pairs",
    "is_rtl",
    "get_supported_scripts",
    "get_supported_script_pairs",
    # Grammar
    "get_grammar_engine",
    "grammar_rules",
    "explain_rule",
    "GrammarEngine",
    "GrammarRule",
    # Morphology
    "analyze_word",
    "generate_forms",
    "list_documented_affixes",
    "lemmatize",
    "WordAnalysis",
    # Dialects
    "list_dialect_profiles",
    "get_dialect_profile",
    "compare_variants",
    "DialectProfile",
    # Literature & Books
    "list_books",
    "get_book",
    "get_page",
    "search_books",
    "register_book",
    "import_book_file",
    "reset_registry",
    "Book",
    "BookMetadata",
    "BookPage",
    "BookSearchResult",
    "LiteratureOverview",
    "get_literature_overview",
    "search_all_literature",
    # Epics
    "Epic",
    "EpicKandaParva",
    "EpicChapter",
    "EpicVerse",
    "list_epics",
    "get_epic",
    "get_epic_chapter",
    "get_epic_verse",
    "search_epics",
    "register_epic",
    "reset_epics_registry",
    # Poetry & Folk Stories
    "Poem",
    "PoemVerse",
    "list_poems",
    "get_poem",
    "search_poetry",
    "list_poetic_forms",
    "FolkStory",
    "FolkStorySection",
    "list_stories",
    "get_story",
    "search_stories",
    # Traditional Songs & Lyrics
    "SongRecord",
    "SongLyricVerse",
    "list_songs",
    "get_song",
    "search_songs",
    "list_song_categories",
    "get_song_lyrics",
    "search_lyrics",
    "format_multiscript_lyrics",
    # Audio & Speech
    "AudioRecording",
    "SpeakerDemographics",
    "AudioQuality",
    "RecordingPermission",
    "get_audio_recording",
    "list_audio_recordings",
    "register_audio_recording",
    # Numbers
    "to_words",
    "parse_words",
    "ordinal_to_words",
    # Pronunciation
    "get_phonetics",
    "get_audio",
    "PhoneticInfo",
    "AudioReference",
    # Culture, Folklore & Proverbs
    "list_proverbs",
    "list_items",
    "search_culture",
    "get_cultural_item",
    "list_cultural_categories",
    "CulturalItem",
    "get_proverb",
    "search_proverbs",
    "Riddle",
    "PastoralCustom",
    "list_riddles",
    "get_riddle",
    "list_customs",
    "search_folklore",
    # Historical Knowledge
    "HistoricalPlace",
    "TribalClan",
    "list_historical_places",
    "list_tribal_clans",
    "search_historical_knowledge",
    # NLP & Corpus
    "tokenize",
    "sent_tokenize",
    "pos_tag",
    "get_ngrams",
    "spell_check",
    "text_similarity",
    "detect_language",
    "stem",
    "Corpus",
    "CorpusStatistics",
    "get_corpus",
    "get_corpus_statistics",
    "concordance",
    # Contributors & Verification
    "Contributor",
    "list_contributors",
    "get_contributor",
    "register_contributor",
    "Submission",
    "AuditLogEntry",
    "submit_entry",
    "review_submission",
    "get_submission",
    "list_submissions",
    "get_audit_history",
    # Universal Search
    "universal_search",
    # Translation
    "translate",
    "TranslationResult",
    # Datasets
    "get_dataset_stats",
    "validate",
    "import_file",
    "export_file",
    "ValidationReport",
    "ImportReport",
    # Exceptions
    "GojriLangError",
    "WordNotFoundError",
    "UnsupportedScriptError",
    "UnsupportedTransliterationError",
    "RuleNotFoundError",
    "DataSchemaValidationError",
    "DatasetValidationError",
    "InvalidDialectError",
    "DialectProfileNotFoundError",
    "BookNotFoundError",
    "EpicNotFoundError",
    "PoemNotFoundError",
    "StoryNotFoundError",
    "SongNotFoundError",
    "AudioResourceNotFoundError",
    "ContributorNotFoundError",
    "VerificationWorkflowError",
    "UnsupportedNumberRangeError",
]
