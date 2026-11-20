"""GojriLang: A Python NLP and Language Preservation Toolkit for Gujari / Gojri.

Gojri (ISO 639-3: gju) is an Indo-Aryan language spoken across Jammu & Kashmir,
Himachal Pradesh, parts of Punjab, Rajasthan, and adjacent northwestern regions.

This library provides an evidence-based computational foundation for Gojri
lexicography, text normalization, transliteration, descriptive grammar,
morphology, oral heritage preservation, literature access, dialect profiling,
numerical counting, and phonetic analysis.
"""

from __future__ import annotations

from typing import List, Optional

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
from gojrilang.culture import (
    CulturalItem,
    get_cultural_item,
    list_cultural_categories,
    list_items,
    list_proverbs,
    list_songs,
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
from gojrilang.grammar import (
    GrammarEngine,
    GrammarRule,
    explain_rule,
    get_grammar_engine,
    grammar_rules,
)
from gojrilang.morphology import (
    WordAnalysis,
    analyze_word,
    generate_forms,
    lemmatize,
    list_documented_affixes,
)
from gojrilang.normalize import (
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
from gojrilang.pronunciation import (
    AudioReference,
    PhoneticInfo,
    get_audio,
    get_phonetics,
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

__version__ = "0.2.0"
__all__ = [
    "__version__",
    # Storage & DB
    "GojriLexiconDB",
    # Dictionary
    "lookup",
    "lookup_all",
    "search",
    "find_synonyms",
    "get_word_details",
    "get_word_variants",
    "DictionaryEntry",
    "ExampleSentence",
    # Text processing & Normalization
    "normalize",
    "normalize_spelling",
    "detect_script",
    "strip_diacritics",
    "normalize_for_search",
    # Transliteration & Romanization
    "transliterate",
    "romanize",
    "supported_transliteration_pairs",
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
    # Numbers
    "to_words",
    "parse_words",
    "ordinal_to_words",
    # Pronunciation
    "get_phonetics",
    "get_audio",
    "PhoneticInfo",
    "AudioReference",
    # Culture
    "list_proverbs",
    "list_songs",
    "list_items",
    "search_culture",
    "get_cultural_item",
    "list_cultural_categories",
    "CulturalItem",
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
    "UnsupportedNumberRangeError",
]
