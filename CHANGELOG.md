# Changelog

All notable changes to **GojriLang** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - Advanced NLP, Literature, Dialects & Developer Ecosystem

### Added
- **Dialect & Regional Variation Engine (`gojrilang.dialects`)**:
  - Structured regional dialect profiles: `jk_poonchi` (Jammu & Kashmir / Poonchi-Rajouri), `western_hazara` (Khyber Pakhtunkhwa / Hazara-Swat), `himachal` (Himachal Pradesh / Kangra-Chamba), `southern_rajasthani` (Rajasthan / Mewat-Marwar).
  - Dialect variant comparison across documented forms: `compare_variants()`.
  - Dialect profile retrieval and querying: `list_dialect_profiles()`, `get_dialect_profile()`.
- **Literature & Historical Corpus Collection (`gojrilang.books`)**:
  - Catalog of authentic historical Gojri literature and linguistic surveys (Grierson 1908 LSI, Sharma 1982 CIIL narratives, Losey 2002 SIL dialogues and proverbs).
  - Page-level retrieval with parallel Perso-Arabic, Devanagari, and Roman transcriptions plus English translations.
  - Multi-book text search: `search_books()`, `list_books()`, `get_book()`, `get_page()`.
- **Numerical Counting & Ordinal System (`gojrilang.numbers`)**:
  - Cardinal number to word conversion for range 0–100: `to_words()`, supporting Perso-Arabic, Devanagari, and Academic Roman scripts.
  - Word-to-integer expression parser: `parse_words()`.
  - Gendered ordinal number generator with irregular (1st–6th) and regular (7th–100th) formations: `ordinal_to_words()`.
  - Strict range validation with `UnsupportedNumberRangeError` preventing speculative numbers.
- **Phonetics, Pronunciation & Audio Metadata (`gojrilang.pronunciation`)**:
  - IPA phonetic transcription, phonetic spelling, tone classification, and syllable segmentation: `get_phonetics()`.
  - Authentic audio recording metadata references: `get_audio()`.
  - Integration with dictionary headwords, alternative spellings, and entry IDs.
- **Advanced Multilingual Lexicon (`gojrilang.dictionary`)**:
  - Levenshtein-distance fuzzy search, prefix search, and multi-field exact search.
  - Expanded dictionary schema: `alternative_spellings`, `definitions`, `synonyms`, `antonyms`, `related_terms`, `pronunciation` (IPA, tone, phonetics), `grammatical_info`, `license`.
  - New dictionary APIs: `lookup_all()`, `find_synonyms()`, `get_word_details()`, `get_word_variants()`.
- **Advanced Grammar Knowledge Base (`gojrilang.grammar`)**:
  - Expanded grammar rule catalog from 12 to 18 verified rules, covering reduplication/echo words (`RULE_REDUPL_01`), interrogatives (`RULE_INTERROG_01`), imperatives (`RULE_IMPER_01`), agreement concord (`RULE_AGREE_01`), derivational morphology (`RULE_WORDFORM_01`), and relative clauses (`RULE_CLAUSE_01`).
  - Educational explanation formatting: `explain_rule()`.
- **Morphology Enhancements (`gojrilang.morphology`)**:
  - Canonical lemmatization engine: `lemmatize()`.
  - Affix-to-grammar-rule provenance tracking in `DOCUMENTED_AFFIXES` and `analyze_word()`.
- **Dataset Management & Tooling (`gojrilang.datasets`)**:
  - Comprehensive schema validation: `validate()` for JSON, JSONL, and CSV files.
  - Batch dataset import with conflict resolution (`skip`, `overwrite`, `fail`): `import_file()`.
  - Multi-format dataset export to JSON, JSONL, and CSV: `export_file()`.
- **Scalable Indexed SQLite & FTS5 Backend (`gojrilang.storage`)**:
  - High-performance SQLite engine with FTS5 virtual tables (`GojriLexiconDB`) capable of indexing 200,000+ words.
  - Sub-millisecond B-tree lookups and full-text search.
- **CLI Subcommands (`gojri`)**:
  - Added `gojri dialects` (list, show, compare).
  - Added `gojri books` (list, show, read, search).
  - Added `gojri numbers` (to-words, parse, ordinal).
  - Added `gojri pronunciation` (show).
  - Added `gojri dataset` (validate, export, import).
  - Added `gojri grammar explain` and `gojri morphology lemmatize`.
- **Expanded Test Suite**:
  - 125 automated unit tests across 13 test modules (`test_books`, `test_dialects`, `test_numbers`, `test_pronunciation`, `test_datasets_mgmt`, etc.) with 100% pass rate.

---

## [0.1.0] - Initial Release

### Added
- **Core Package**: Initial release of `gojrilang` Python toolkit for Gojri (ISO 639-3: `gju`).
- **Multilingual Dictionary (`gojrilang.dictionary`)**:
  - Searchable lexicon across Perso-Arabic, Devanagari, and Academic Roman.
  - Multilingual meanings in English, Hindi, and Urdu.
  - POS tags, gender tagging, dialect notes, and authenticated example sentences.
  - `lookup()` and `search()` functions with case-insensitive and diacritic-insensitive matching.
- **Text Processing & Transliteration (`gojrilang.normalize`, `gojrilang.transliteration`)**:
  - Script detection for Perso-Arabic, Devanagari, and Latin/Roman.
  - Unicode NFC/NFKC normalization, whitespace collapsing, punctuation alignment.
  - Tashkeel/harakat and diacritic stripping.
  - Validated bidirectional transliteration between Perso-Arabic, Devanagari, and Roman scripts.
  - Clear `UnsupportedTransliterationError` for unvalidated conversions.
- **Grammar Engine (`gojrilang.grammar`)**:
  - Structured catalog of verified Gojri grammar rules based on J.C. Sharma (1982) and Wayne Losey (2002).
  - Rule categorization: phonology, nouns/pronouns, verbs, TAM, negation, postpositions/split-ergativity, syntax, dialect variation.
  - Rule-assisted experimental sentence analysis (`analyze_sentence()`).
- **Morphology Subsystem (`gojrilang.morphology`)**:
  - Root extraction, affix identification, and morphological segmentation (`analyze_word()`).
  - Evidence-based paradigm generator for marked masculine/feminine nouns and regular verbs (`generate_forms()`).
- **Cultural & Oral Heritage Preservation (`gojrilang.culture`)**:
  - Curated database of Gojri proverbs (*Akhan*), idioms, and pastoral transhumance terminology.
  - Contextual explanations, regional provenance, and source citations (Dr. Javaid Rahi / JKAACL).
- **Translation Subsystem (`gojrilang.translation`)**:
  - Verified phrase translation between Gojri, English, Hindi, and Urdu.
  - Explicit status reporting (`exact_match`, `lexical_match`, `not_found`, `unsupported_pair`) avoiding hallucinatory ML output.
- **Command-Line Interface (`gojri`)**:
  - Complete CLI supporting `lookup`, `search`, `normalize`, `transliterate`, `grammar`, `morphology`, `culture`, `translate`, `stats`, and `info`.
  - JSON output flag `--json` for machine readability and scripting.
- **Test Suite**:
  - Comprehensive unit tests covering dictionary, search, normalization, transliteration, grammar, morphology, culture, translation, CLI, and dataset validation.

