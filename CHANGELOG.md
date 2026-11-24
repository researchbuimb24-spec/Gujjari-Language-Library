# Changelog

All notable changes to **GojriLang** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - Complete Modular Architecture & Digital Heritage Infrastructure

### Added
- **Epic Literature Subsystem (`gojrilang.epics`)**:
  - Structured support for Gojri oral epic traditions: *Gojri Ramayana* (7 Kandas: Bal, Ayodhya, Aranya, Kishkindha, Sundara, Yuddha, Uttara) and *Gojri Mahabharata* (5 Parvas: Adi, Vana, Virata, Bhishma, Shanti).
  - Verse-level multiscript transcriptions (Perso-Arabic, Devanagari, Academic Roman), English/Hindi/Urdu translations, vocabulary extraction, and cultural notes.
  - Epic APIs: `list_epics()`, `get_epic()`, `get_epic_chapter()`, `get_epic_verse()`, `search_epics()`, `register_epic()`.
- **Music & Oral Songs Archive (`gojrilang.songs`, `gojrilang.lyrics`)**:
  - Musicological catalog covering 8 documented genres: Chhaint, Mahya, Singran Ka Geet (caravan chants), Bait, Lori (lullabies), Dholak De Geet (wedding melodies), Baranmah (calendar verses), and Gwali (highland shepherd calls).
  - Multiscript lyrics alignment, musical instrument documentation (alghoza, bansuri, dholak, chimta, sarangi), rhythm and raga associations.
  - APIs: `list_songs()`, `get_song()`, `search_songs()`, `list_song_categories()`, `get_song_lyrics()`, `format_multiscript_lyrics()`, `search_lyrics()`.
- **Classical & Sufi Poetry Subsystem (`gojrilang.poetry`)**:
  - Documented Gojri poetic forms: Bait, Si-Harfi, Kafi, Ghazal, Dohra, and Nazm.
  - Featured poets: Hazrat Mian Nizam-ud-Din Larvi, Sain Qadir Bakhsh, Khuda Bakhsh Zaar.
  - APIs: `list_poems()`, `get_poem()`, `search_poetry()`, `list_poetic_forms()`.
- **Folktales & Oral Dastans (`gojrilang.folk_stories`)**:
  - Dastan-e-Sohni Mahiwal (pastoral Chenab legend), Charwaho te Sher (shepherd courage), Kissa Roop Basant (fraternal devotion).
  - APIs: `list_stories()`, `get_story()`, `search_stories()`.
- **Unified Digital Literature Archive (`gojrilang.literature`)**:
  - Unified entry point consolidating books, epics, poetry, and folktales.
  - APIs: `get_literature_overview()`, `search_all_literature()`.
- **Folklore, Riddles & Pastoral Traditions (`gojrilang.folklore`, `gojrilang.proverbs`)**:
  - Traditional riddles (*Pahaṇḍi* / *Bujhārat*) and seasonal transhumance customs (*Bahak Chal*, *Dhooni Baal*).
  - Dedicated proverb interface: `list_proverbs()`, `get_proverb()`, `search_proverbs()`.
  - APIs: `list_riddles()`, `get_riddle()`, `list_customs()`, `search_folklore()`.
- **Historical Knowledge & Clans (`gojrilang.historical_knowledge`)**:
  - Documented historical settlements and tribal clans (Khatana, Poswal, Chauhan, Bajran, Chechi, Awana).
  - APIs: `list_historical_places()`, `list_tribal_clans()`, `search_historical_knowledge()`.
- **Computational NLP Subsystem (`gojrilang.nlp`)**:
  - Multiscript tokenization (`tokenize()`) and sentence segmentation (`sent_tokenize()`).
  - Rule-assisted baseline part-of-speech tagger (`pos_tag()`).
  - N-gram generator (`get_ngrams()`).
  - Spell checking with Levenshtein-candidate ranking (`spell_check()`).
  - Jaccard and Levenshtein text similarity metrics (`text_similarity()`).
  - Gojri language identification with diagnostic marker detection (`detect_language()`).
  - Rule-based stemmer (`stem()`).
- **Corpus Analytics & KWIC Concordances (`gojrilang.corpus`)**:
  - Full-corpus quantitative metrics: tokens, unique types, sentences, type-token ratio (TTR), hapax legomena count, frequency distribution.
  - Key-Word-In-Context (KWIC) concordance tables with configurable context windows.
  - APIs: `get_corpus()`, `get_corpus_statistics()`, `concordance()`.
- **Audio & Speech Infrastructure (`gojrilang.audio`)**:
  - Metadata models for speech recordings: speaker demographics, recording permissions, audio quality tiers, dialectal regions.
  - APIs: `get_audio_recording()`, `list_audio_recordings()`, `register_audio_recording()`.
- **Verification Workflow & Contributor Registry (`gojrilang.verification`, `gojrilang.contributors`)**:
  - Five-stage verification lifecycle: `community_submitted` -> `needs_review` -> `under_review` -> `verified` / `rejected`.
  - Role-based permissions preventing unauthorized self-verification.
  - Immutable audit trail logging: `get_audit_history()`.
  - Contributor registry with affiliation and dialect expertise.
- **Unified Object-Oriented Facade (`Gojri`)**:
  - Comprehensive `from gojrilang import Gojri; gju = Gojri()` facade exposing all 13 sub-namespaces (`dictionary`, `grammar`, `scripts`, `dialects`, `literature`, `epics`, `songs`, `folklore`, `corpus`, `nlp`, `audio`, `verification`, `vocabulary`).
- **Enhanced Dual CLI (`gojri` and `gojrilang`)**:
  - Added CLI subcommands: `epics`, `songs`, `folklore`, `corpus`, `nlp`, `literature`, `dictionary`.
  - Direct workflow commands: `validate-data`, `import-data`, `verify-data`, `export-corpus`.
- **Testing & Quality Assurance**:
  - Expanded test suite from 145 to 206 automated unit tests with 100% pass rate.
  - Validated packaging distribution: `.whl` and `.tar.gz`.

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

