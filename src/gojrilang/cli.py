"""Command-line interface (CLI) for GojriLang toolkit.

Entry point: 'gojri'
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

import gojrilang
from gojrilang.culture import list_proverbs, search_culture
from gojrilang.datasets import get_dataset_stats
from gojrilang.dictionary import lookup, search
from gojrilang.exceptions import GojriLangError
from gojrilang.grammar import get_grammar_engine
from gojrilang.morphology import analyze_word, generate_forms
from gojrilang.normalize import detect_script, normalize
from gojrilang.storage import GojriLexiconDB
from gojrilang.translation import translate
from gojrilang.transliteration import transliterate


def _print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_lookup(args: argparse.Namespace) -> int:
    entry = lookup(args.word, dialect=args.dialect)
    if not entry:
        print(f"Error: Word '{args.word}' was not found in the verified dictionary.", file=sys.stderr)
        return 1

    if args.json:
        _print_json(entry.to_dict())
    else:
        print(f"\n--- Entry: {entry.word} ---")
        if entry.word_roman:
            print(f"Roman:       {entry.word_roman}")
        if entry.word_devanagari:
            print(f"Devanagari:  {entry.word_devanagari}")
        print(f"Part of Speech: {entry.pos}" + (f" ({entry.gender})" if entry.gender else ""))
        print(f"English:     {entry.meaning_en}")
        print(f"Hindi:       {entry.meaning_hi}")
        print(f"Urdu:        {entry.meaning_ur}")
        print(f"Dialect:     {entry.dialect}")
        print(f"Status:      {entry.verification_status}")
        print(f"Source:      {entry.source}")
        if entry.example_sentence:
            ex = entry.example_sentence
            print(f"Example:     {ex.text}")
            if ex.text_roman:
                print(f"             ({ex.text_roman})")
            print(f"             EN: {ex.translation_en}")
            print(f"             HI: {ex.translation_hi}")
            print(f"             UR: {ex.translation_ur}")
        if entry.notes:
            print(f"Notes:       {entry.notes}")
        print()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    results = search(
        query=args.query,
        language=args.language,
        pos=args.pos,
        dialect=args.dialect,
        limit=args.limit,
    )
    if not results:
        print(f"No dictionary records found matching '{args.query}'.")
        return 0

    if args.json:
        _print_json([r.to_dict() for r in results])
    else:
        print(f"\nFound {len(results)} match(es) for '{args.query}':\n")
        for idx, entry in enumerate(results, 1):
            rom = f" ({entry.word_roman})" if entry.word_roman else ""
            print(f"{idx}. {entry.word}{rom} [{entry.pos}]")
            print(f"   EN: {entry.meaning_en}")
            print(f"   HI: {entry.meaning_hi}")
            print(f"   UR: {entry.meaning_ur}")
            print(f"   Status: {entry.verification_status} | Source: {entry.source}")
        print()
    return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    norm = normalize(args.text, remove_diacritics=args.remove_diacritics)
    script = detect_script(args.text)
    if args.json:
        _print_json({
            "original": args.text,
            "normalized": norm,
            "detected_script": script,
            "diacritics_removed": args.remove_diacritics,
        })
    else:
        print(norm)
    return 0


def cmd_transliterate(args: argparse.Namespace) -> int:
    try:
        out = transliterate(args.text, source=args.source, target=args.target)
        if args.json:
            _print_json({
                "original": args.text,
                "source_script": args.source,
                "target_script": args.target,
                "transliterated": out,
            })
        else:
            print(out)
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_grammar_list(args: argparse.Namespace) -> int:
    engine = get_grammar_engine()
    rules = engine.list_rules(category=args.category, status=args.status)
    if args.json:
        _print_json([r.to_dict() for r in rules])
    else:
        print(f"\nDocumented Gojri Grammar Rules ({len(rules)}):\n")
        for r in rules:
            print(f"• [{r.id}] ({r.category}) {r.name} [{r.verification_status}]")
            print(f"    Dialect: {r.dialect} | Source: {r.source}")
        print()
    return 0


def cmd_grammar_show(args: argparse.Namespace) -> int:
    engine = get_grammar_engine()
    try:
        r = engine.get_rule(args.rule_id)
        if args.json:
            _print_json(r.to_dict())
        else:
            print(f"\n--- Rule: {r.id} ---")
            print(f"Name:        {r.name}")
            print(f"Category:    {r.category}")
            print(f"Dialect:     {r.dialect}")
            print(f"Status:      {r.verification_status}")
            print(f"Source:      {r.source}")
            print(f"Description: {r.description}\n")
            print("Examples:")
            for ex in r.examples:
                rom = f" ({ex.get('roman')})" if ex.get("roman") else ""
                print(f"  • {ex.get('gojri')}{rom}: {ex.get('translation_en')}")
            print()
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_grammar_explain(args: argparse.Namespace) -> int:
    try:
        text = gojrilang.explain_rule(args.rule_id)
        print(f"\n{text}\n")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_grammar_analyze(args: argparse.Namespace) -> int:
    engine = get_grammar_engine()
    analysis = engine.analyze_sentence(args.sentence)
    if args.json:
        _print_json(analysis)
    else:
        print(f"\nSentence Diagnostics ({analysis['status']}):")
        print(f"Sentence: '{analysis['sentence']}' [Script: {analysis['script']}]")
        print(f"Tokens:   {', '.join(analysis['tokens'])}")
        if analysis["postpositions"]:
            print("\nIdentified Postpositions:")
            for p in analysis["postpositions"]:
                print(f"  - '{p['token']}' -> {p['description']}")
        if analysis["pronouns"]:
            print("\nIdentified Pronouns:")
            for pr in analysis["pronouns"]:
                print(f"  - '{pr['token']}' -> {pr['description']}")
        if analysis["diagnostics"]:
            print("\nGrammatical Observations:")
            for d in analysis["diagnostics"]:
                print(f"  [{d['type'].upper()}] {d['observation']}")
        print(f"\nNote: {analysis['notes']}\n")
    return 0


def cmd_morphology_analyze(args: argparse.Namespace) -> int:
    ana = analyze_word(args.word)
    if args.json:
        _print_json(ana.to_dict())
    else:
        print(f"\nMorphology Analysis for '{args.word}':")
        print(f"Script:              {ana.script}")
        print(f"Lemma:               {ana.lemma or 'N/A'}")
        print(f"POS:                 {ana.pos or 'N/A'}")
        print(f"Gender:              {ana.gender or 'N/A'}")
        print(f"Number:              {ana.number or 'N/A'}")
        print(f"Case:                {ana.case or 'N/A'}")
        print(f"Stem:                {ana.stem or 'N/A'}")
        print(f"Verification Status: {ana.verification_status}")
        if ana.affixes:
            print("Affixes:")
            for af in ana.affixes:
                rule_note = f" [{af['rule_id']}]" if "rule_id" in af else ""
                print(f"  • {af['affix']} ({af['function']}){rule_note}")
        print()
    return 0


def cmd_morphology_generate(args: argparse.Namespace) -> int:
    try:
        forms = generate_forms(args.root, category=args.category, dialect=args.dialect)
        if args.json:
            _print_json({
                "root": args.root,
                "category": args.category,
                "forms": forms,
            })
        else:
            print(f"\nGenerated Forms for '{args.root}' ({args.category}):\n")
            for slot, val in forms.items():
                print(f"  {slot:20}: {val}")
            print()
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_morphology_lemmatize(args: argparse.Namespace) -> int:
    lem = gojrilang.lemmatize(args.word)
    if args.json:
        _print_json({"word": args.word, "lemma": lem})
    else:
        print(f"Lemma for '{args.word}': {lem or 'N/A'}")
    return 0


def cmd_culture_list(args: argparse.Namespace) -> int:
    proverbs = list_proverbs()
    if args.json:
        _print_json([p.to_dict() for p in proverbs])
    else:
        print(f"\nVerified Gojri Proverbs ({len(proverbs)}):\n")
        for idx, p in enumerate(proverbs, 1):
            rom = f" ({p.text_roman})" if p.text_roman else ""
            print(f"{idx}. {p.text}{rom}")
            print(f"   EN: {p.translation_en}")
            print(f"   HI: {p.translation_hi}")
            print(f"   UR: {p.translation_ur}")
            print(f"   Region: {p.region} | Source: {p.source}\n")
    return 0


def cmd_culture_search(args: argparse.Namespace) -> int:
    items = search_culture(args.term, category=args.category, limit=args.limit)
    if not items:
        print(f"No cultural heritage records found matching '{args.term}'.")
        return 0

    if args.json:
        _print_json([i.to_dict() for i in items])
    else:
        print(f"\nFound {len(items)} cultural item(s) for '{args.term}':\n")
        for idx, item in enumerate(items, 1):
            rom = f" ({item.text_roman})" if item.text_roman else ""
            print(f"{idx}. [{item.category.upper()}] {item.text}{rom} - '{item.title}'")
            print(f"   EN: {item.translation_en}")
            print(f"   Explanation: {item.explanation}")
            print(f"   Region: {item.region} | Source: {item.source}\n")
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    res = gojrilang.translate(args.text, source=args.source, target=args.target)
    if args.json:
        _print_json(res.to_dict())
    else:
        print(f"\nTranslation ({res.source} -> {res.target}) [{res.status}]:")
        print(f"Output:     {res.text}")
        print(f"Confidence: {res.confidence}")
        if res.notes:
            print(f"Notes:      {res.notes}")
        print()
    return 0


def cmd_dialects_list(args: argparse.Namespace) -> int:
    profiles = gojrilang.list_dialect_profiles()
    if args.json:
        _print_json([p.to_dict() for p in profiles])
    else:
        print(f"\nDocumented Gojri Dialect Profiles ({len(profiles)}):\n")
        for p in profiles:
            print(f"• [{p.id}] {p.name} - {p.region}")
            print(f"    Sub-dialects: {', '.join(p.sub_dialects)}")
            print(f"    Features:     {len(p.phonological_features)} phonological, {len(p.lexical_variants)} lexical")
        print()
    return 0


def cmd_dialects_show(args: argparse.Namespace) -> int:
    try:
        p = gojrilang.get_dialect_profile(args.profile_id)
        if args.json:
            _print_json(p.to_dict())
        else:
            print(f"\n--- Dialect Profile: {p.name} [{p.id}] ---")
            print(f"Region:                {p.region}")
            print(f"Sub-dialects:          {', '.join(p.sub_dialects)}")
            print(f"Phonological Features: {', '.join(p.phonological_features)}")
            print("Documented Lexical Variants:")
            for k, v in p.lexical_variants.items():
                print(f"  • {k:15} -> {v}")
            print(f"References:            {', '.join(p.references)}\n")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_dialects_compare(args: argparse.Namespace) -> int:
    diff = gojrilang.compare_variants(args.word, profiles=args.profiles)
    if args.json:
        _print_json(diff)
    else:
        print(f"\nDialect Comparison for '{args.word}':")
        for prof_id, var in diff.items():
            print(f"  • {prof_id:20}: {var}")
        print()
    return 0


def cmd_books_list(args: argparse.Namespace) -> int:
    books = gojrilang.list_books()
    if args.json:
        _print_json([b.to_dict() for b in books])
    else:
        print(f"\nDocumented Gojri Literature Collections ({len(books)}):\n")
        for b in books:
            print(f"• [{b.id}] {b.title}")
            print(f"    Author: {b.author} ({b.year}) | Dialect: {b.dialect} | {b.page_count} page(s)")
            print(f"    License: {b.license}")
        print()
    return 0


def cmd_books_show(args: argparse.Namespace) -> int:
    try:
        book = gojrilang.get_book(args.book_id)
        if args.json:
            _print_json(book.to_dict())
        else:
            meta = book.metadata
            print(f"\n--- Book: {meta.title} ---")
            print(f"ID:          {meta.id}")
            print(f"Author:      {meta.author} ({meta.year})")
            print(f"Publisher:   {meta.publisher}")
            print(f"Dialect:     {meta.dialect}")
            print(f"License:     {meta.license}")
            print(f"Description: {meta.description}")
            print(f"Pages:       {meta.page_count}\n")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_books_read(args: argparse.Namespace) -> int:
    try:
        page = gojrilang.get_page(args.book_id, args.page_number)
        if args.json:
            _print_json(page.to_dict())
        else:
            print(f"\n--- {args.book_id} (Page {page.page_number}) ---")
            print(f"Section: {page.section_title}\n")
            print(f"Perso-Arabic:\n  {page.text_perso_arabic}\n")
            if page.text_devanagari:
                print(f"Devanagari:\n  {page.text_devanagari}\n")
            if page.text_roman:
                print(f"Roman:\n  {page.text_roman}\n")
            print(f"English Translation:\n  {page.translation_en}\n")
            if page.notes:
                print(f"Linguistic Notes:\n  {page.notes}\n")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_books_search(args: argparse.Namespace) -> int:
    results = gojrilang.search_books(args.term)
    if args.json:
        _print_json([r.to_dict() for r in results])
    else:
        print(f"\nFound {len(results)} match(es) for '{args.term}' in Gojri literature:\n")
        for idx, r in enumerate(results, 1):
            print(f"{idx}. [{r.book_id} p.{r.page_number}] {r.section_title}")
            print(f"   Field: {r.matched_field}")
            print(f"   Snippet: {r.snippet}\n")
    return 0


def cmd_numbers_to_words(args: argparse.Namespace) -> int:
    try:
        words = gojrilang.to_words(args.number, script=args.script)
        if args.json:
            _print_json({"number": args.number, "script": args.script, "words": words})
        else:
            print(f"{args.number} -> {words}")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_numbers_parse(args: argparse.Namespace) -> int:
    try:
        val = gojrilang.parse_words(args.expression)
        if args.json:
            _print_json({"expression": args.expression, "parsed": val})
        else:
            print(f"'{args.expression}' -> {val}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_numbers_ordinal(args: argparse.Namespace) -> int:
    try:
        words = gojrilang.ordinal_to_words(args.number, gender=args.gender, script=args.script)
        if args.json:
            _print_json({"number": args.number, "gender": args.gender, "script": args.script, "ordinal": words})
        else:
            print(f"{args.number} ({args.gender}) -> {words}")
        return 0
    except GojriLangError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_pronunciation_show(args: argparse.Namespace) -> int:
    phon = gojrilang.get_phonetics(args.word)
    audio = gojrilang.get_audio(args.word)
    if args.json:
        _print_json({
            "phonetics": phon.to_dict() if phon else None,
            "audio": audio.to_dict() if audio else None,
        })
    else:
        print(f"\nPronunciation & Phonetics for '{args.word}':")
        if phon:
            print(f"IPA:               {phon.ipa}")
            print(f"Phonetic Spelling: {phon.phonetic_spelling}")
            print(f"Syllables:         {phon.syllables}")
            print(f"Tone:              {phon.tone or 'none'}")
            print(f"Dialect:           {phon.dialect}")
            print(f"Status:            {phon.status}")
        if audio:
            print(f"Audio Reference:   {audio.audio_url or 'N/A'}")
            print(f"Recording Status:  {audio.status}")
        print()
    return 0


def cmd_dataset_validate(args: argparse.Namespace) -> int:
    report = gojrilang.validate(args.file, dataset_type=args.type)
    if args.json:
        _print_json(report.to_dict())
    else:
        print(f"\nDataset Validation ({args.file}):")
        print(f"Status:   {'PASSED' if report.is_valid else 'FAILED'}")
        print(f"Records:  {report.total_records}")
        print(f"Errors:   {len(report.errors)}")
        print(f"Warnings: {len(report.warnings)}")
        if report.errors:
            print("\nErrors:")
            for err in report.errors[:10]:
                print(f"  • {err}")
            if len(report.errors) > 10:
                print(f"  ... and {len(report.errors) - 10} more.")
        if report.warnings:
            print("\nWarnings:")
            for w in report.warnings[:5]:
                print(f"  • {w}")
        print()
    return 0 if report.is_valid else 1


def cmd_dataset_export(args: argparse.Namespace) -> int:
    try:
        out = gojrilang.export_file(args.output, dataset_name=args.dataset, fmt=args.format)
        print(f"Successfully exported '{args.dataset}' to '{out}'.")
        return 0
    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        return 1


def cmd_dataset_import(args: argparse.Namespace) -> int:
    try:
        report = gojrilang.import_file(args.file, target_dataset=args.dataset, conflict_resolution=args.conflict)
        if args.json:
            _print_json(report.to_dict())
        else:
            print(f"\nImport Summary for '{args.file}':")
            print(f"Imported:    {report.imported_count}")
            print(f"Skipped:     {report.skipped_count}")
            print(f"Overwritten: {report.overwritten_count}")
            print(f"Errors:      {len(report.errors)}\n")
        return 0
    except Exception as e:
        print(f"Error during import: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    stats = get_dataset_stats()
    if args.json:
        _print_json(stats)
    else:
        print("\n=== GojriLang Corpus Statistics ===")
        print(f"Language:              {stats['language']}")
        print(f"Dictionary Entries:    {stats['dictionary']['total_entries']} (Verified: {stats['dictionary']['verified_count']})")
        print(f"Parts of Speech:       {', '.join(stats['dictionary']['parts_of_speech'])}")
        print(f"Grammar Rules:         {stats['grammar']['total_rules']}")
        print(f"Grammar Categories:    {', '.join(stats['grammar']['categories'])}")
        print(f"Dialect Profiles:      {stats.get('dialects', {}).get('total_profiles', 0)}")
        print(f"Literature Books:      {stats.get('books', {}).get('total_books', 0)} ({stats.get('books', {}).get('total_pages', 0)} pages)")
        print(f"Cultural Items:        {stats['culture']['total_items']}")
        print(f"Translation Pairs:     {stats['translation']['total_phrases']} phrases across {', '.join(stats['translation']['supported_languages'])}")
        print("===================================\n")
    return 0


def cmd_db_build(args: argparse.Namespace) -> int:
    db = GojriLexiconDB(args.db_path)
    count = db.build_from_bundled_data()
    print(f"Successfully built SQLite index at '{db.db_path}' with {count} entries.")
    return 0


def cmd_db_import(args: argparse.Namespace) -> int:
    db = GojriLexiconDB(args.db_path)
    try:
        count = db.import_from_csv(
            filepath=args.file,
            default_source=args.source,
            default_status=args.status,
            default_dialect=args.dialect,
        )
        print(f"Successfully imported {count} records into '{db.db_path}'. Total count: {db.count()}")
        return 0
    except Exception as e:
        print(f"Error during import: {e}", file=sys.stderr)
        return 1


def cmd_db_stats(args: argparse.Namespace) -> int:
    db = GojriLexiconDB(args.db_path)
    print(f"\n=== GojriLexiconDB Indexed Storage ===")
    print(f"Database File:  {db.db_path}")
    print(f"Total Entries:  {db.count()}")
    print("Capable of scaling to 200,000+ words with FTS5 indexing.")
    print("======================================\n")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    print(f"""
GojriLang Toolkit v{gojrilang.__version__}
Preservation and NLP Toolkit for Gujari / Gojri (ISO 639-3: gju)

Scholarly Foundations:
  • Sharma, J. C. (1982). Gojri Grammar. CIIL Mysore.
  • Rahi, Javaid. Gojri Dictionary & Folk-Lore Dictionary. JKAACL.
  • Losey, Wayne E. (2002). Writing Gojri. SIL International.
  • Grierson, G. A. (1908). Linguistic Survey of India, Vol. IX, Part IV.

Run 'gojri --help' for available commands.
""")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gojri",
        description="GojriLang: Python NLP and Digital Preservation Toolkit for Gujari / Gojri.",
    )
    parser.add_argument("--version", action="version", version=f"gojrilang {gojrilang.__version__}")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # lookup
    p_lookup = subparsers.add_parser("lookup", help="Look up a word in the Gojri dictionary.")
    p_lookup.add_argument("word", help="The word to search.")
    p_lookup.add_argument("--dialect", help="Optional dialect filter.")

    # search
    p_search = subparsers.add_parser("search", help="Search dictionary entries.")
    p_search.add_argument("query", help="Keyword or gloss to search for.")
    p_search.add_argument(
        "--language", "-l", default="all",
        choices=["all", "english", "en", "hindi", "hi", "urdu", "ur", "gojri"],
        help="Field/language to search in.",
    )
    p_search.add_argument("--pos", help="Filter by part of speech (noun, verb, etc.).")
    p_search.add_argument("--dialect", help="Filter by dialect.")
    p_search.add_argument("--limit", type=int, default=None, help="Max results.")

    # normalize
    p_norm = subparsers.add_parser("normalize", help="Normalize Gojri text.")
    p_norm.add_argument("text", help="Text to normalize.")
    p_norm.add_argument("--remove-diacritics", action="store_true", help="Strip combining diacritics / harakat.")

    # transliterate
    p_translit = subparsers.add_parser("transliterate", help="Transliterate text between validated scripts.")
    p_translit.add_argument("text", help="Text to transliterate.")
    p_translit.add_argument("--from", dest="source", default=None, help="Source script (perso-arabic, devanagari, roman).")
    p_translit.add_argument("--to", dest="target", default="roman", help="Target script (perso-arabic, devanagari, roman).")

    # grammar
    p_grammar = subparsers.add_parser("grammar", help="Query Gojri grammar rules and sentence diagnostics.")
    g_subs = p_grammar.add_subparsers(dest="grammar_cmd", help="Grammar actions")
    p_g_list = g_subs.add_parser("list", help="List grammar rules.")
    p_g_list.add_argument("--category", help="Category filter.")
    p_g_list.add_argument("--status", help="Status filter (verified, experimental).")
    p_g_show = g_subs.add_parser("show", help="Display details of a specific grammar rule.")
    p_g_show.add_argument("rule_id", help="Rule ID (e.g. RULE_POSTPOS_01).")
    p_g_exp = g_subs.add_parser("explain", help="Display educational explanation of a rule.")
    p_g_exp.add_argument("rule_id", help="Rule ID.")
    p_g_ana = g_subs.add_parser("analyze", help="Perform rule-assisted structural analysis on a sentence.")
    p_g_ana.add_argument("sentence", help="Sentence text.")

    # morphology
    p_morph = subparsers.add_parser("morphology", help="Morphological analysis and paradigm generation.")
    m_subs = p_morph.add_subparsers(dest="morphology_cmd", help="Morphology actions")
    p_m_ana = m_subs.add_parser("analyze", help="Analyze word morphology.")
    p_m_ana.add_argument("word", help="Word to analyze.")
    p_m_gen = m_subs.add_parser("generate", help="Generate inflectional forms from root.")
    p_m_gen.add_argument("root", help="Root or stem.")
    p_m_gen.add_argument("--category", required=True, help="Paradigm category (marked_masculine_noun, marked_feminine_noun, regular_verb).")
    p_m_gen.add_argument("--dialect", default="general", help="Dialect variation.")
    p_m_lem = m_subs.add_parser("lemmatize", help="Find base canonical lemma for a word.")
    p_m_lem.add_argument("word", help="Word to lemmatize.")

    # dialects
    p_dia = subparsers.add_parser("dialects", help="Query regional dialect profiles and compare variants.")
    dia_subs = p_dia.add_subparsers(dest="dialects_cmd", help="Dialect actions")
    dia_subs.add_parser("list", help="List all documented dialect profiles.")
    p_dia_show = dia_subs.add_parser("show", help="Show dialect profile details.")
    p_dia_show.add_argument("profile_id", help="Dialect profile ID (e.g. jk_poonchi, western_hazara).")
    p_dia_comp = dia_subs.add_parser("compare", help="Compare word variants across dialects.")
    p_dia_comp.add_argument("word", help="Base word to compare.")
    p_dia_comp.add_argument("--profiles", nargs="+", help="Optional subset of profile IDs.")

    # books (literature)
    p_books = subparsers.add_parser("books", help="Browse, read, and search historical Gojri literature.")
    b_subs = p_books.add_subparsers(dest="books_cmd", help="Books actions")
    b_subs.add_parser("list", help="List all documented literature collections.")
    p_b_show = b_subs.add_parser("show", help="Show book metadata.")
    p_b_show.add_argument("book_id", help="Book identifier.")
    p_b_read = b_subs.add_parser("read", help="Read a page from a book.")
    p_b_read.add_argument("book_id", help="Book identifier.")
    p_b_read.add_argument("page_number", type=int, help="Page number.")
    p_b_search = b_subs.add_parser("search", help="Search within Gojri literature collections.")
    p_b_search.add_argument("term", help="Search keyword or phrase.")

    # numbers
    p_num = subparsers.add_parser("numbers", help="Gojri numerical counting and ordinal word generation.")
    num_subs = p_num.add_subparsers(dest="numbers_cmd", help="Numbers actions")
    p_num_tw = num_subs.add_parser("to-words", help="Convert integer (0-100) to Gojri words.")
    p_num_tw.add_argument("number", type=int, help="Number between 0 and 100.")
    p_num_tw.add_argument("--script", default="roman", help="Target script (roman, perso-arabic, devanagari).")
    p_num_p = num_subs.add_parser("parse", help="Parse number in words to integer.")
    p_num_p.add_argument("expression", help="Gojri number words (e.g. 'hik', 'vīh', 'پنجاہ').")
    p_num_ord = num_subs.add_parser("ordinal", help="Generate ordinal number in words.")
    p_num_ord.add_argument("number", type=int, help="Number between 1 and 100.")
    p_num_ord.add_argument("--gender", default="masculine", help="Gender (masculine, feminine).")
    p_num_ord.add_argument("--script", default="roman", help="Target script (roman, perso-arabic, devanagari).")

    # pronunciation
    p_pron = subparsers.add_parser("pronunciation", help="Query IPA phonetics, syllable count, tone, and audio.")
    pron_subs = p_pron.add_subparsers(dest="pronunciation_cmd", help="Pronunciation actions")
    p_pron_show = pron_subs.add_parser("show", help="Show phonetics and audio reference for a word.")
    p_pron_show.add_argument("word", help="Word or entry ID.")

    # dataset
    p_ds = subparsers.add_parser("dataset", help="Dataset management, validation, import, and export.")
    ds_subs = p_ds.add_subparsers(dest="dataset_cmd", help="Dataset actions")
    p_ds_val = ds_subs.add_parser("validate", help="Validate a dataset file.")
    p_ds_val.add_argument("file", help="Path to dataset file.")
    p_ds_val.add_argument("--type", default="dictionary", help="Dataset type (dictionary).")
    p_ds_exp = ds_subs.add_parser("export", help="Export a dataset.")
    p_ds_exp.add_argument("output", help="Output destination file path.")
    p_ds_exp.add_argument("--dataset", default="dictionary", help="Dataset name (dictionary, grammar, culture, translation, dialects, books).")
    p_ds_exp.add_argument("--format", default="auto", choices=["auto", "json", "jsonl", "csv"], help="Export format.")
    p_ds_imp = ds_subs.add_parser("import", help="Import a validated dataset file.")
    p_ds_imp.add_argument("file", help="Path to input dataset file.")
    p_ds_imp.add_argument("--dataset", default="dictionary", help="Target dataset.")
    p_ds_imp.add_argument("--conflict", default="skip", choices=["skip", "overwrite", "fail"], help="Conflict resolution.")

    # culture
    p_cult = subparsers.add_parser("culture", help="Browse and search Gojri cultural heritage and proverbs.")
    c_subs = p_cult.add_subparsers(dest="culture_cmd", help="Culture actions")
    p_c_list = c_subs.add_parser("list", help="List verified proverbs.")
    p_c_search = c_subs.add_parser("search", help="Search cultural terms and proverbs.")
    p_c_search.add_argument("term", help="Search keyword.")
    p_c_search.add_argument("--category", help="Category filter (proverbs, pastoral_terms).")
    p_c_search.add_argument("--limit", type=int, default=None, help="Max results.")

    # translate
    p_trans = subparsers.add_parser("translate", help="Translate phrases between Gojri, English, Hindi, and Urdu.")
    p_trans.add_argument("text", help="Text to translate.")
    p_trans.add_argument("--from", dest="source", default="gojri", help="Source language (gojri, english, hindi, urdu).")
    p_trans.add_argument("--to", dest="target", default="english", help="Target language (gojri, english, hindi, urdu).")

    # db (SQLite / FTS scalable backend)
    p_db = subparsers.add_parser("db", help="Scalable indexed database operations (up to 200,000+ words).")
    db_subs = p_db.add_subparsers(dest="db_cmd", help="Database actions")
    p_db_build = db_subs.add_parser("build", help="Build/rebuild SQLite index from verified bundled data.")
    p_db_build.add_argument("--db-path", default="gojri_lexicon.db", help="Path to database file.")
    p_db_import = db_subs.add_parser("import", help="Import words from CSV into indexed database.")
    p_db_import.add_argument("file", help="Path to CSV file.")
    p_db_import.add_argument("--db-path", default="gojri_lexicon.db", help="Path to database file.")
    p_db_import.add_argument("--source", default="Community Contribution", help="Attribution source.")
    p_db_import.add_argument("--status", default="community_reviewed", help="Verification status.")
    p_db_import.add_argument("--dialect", default="general", help="Dialect name.")
    p_db_stats = db_subs.add_parser("stats", help="Show database record counts and status.")
    p_db_stats.add_argument("--db-path", default="gojri_lexicon.db", help="Path to database file.")

    # stats & info
    subparsers.add_parser("stats", help="Display verified corpus statistics.")
    subparsers.add_parser("info", help="Display library metadata and scholarly provenance.")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 0

    if args.subcommand == "lookup":
        return cmd_lookup(args)
    elif args.subcommand == "search":
        return cmd_search(args)
    elif args.subcommand == "normalize":
        return cmd_normalize(args)
    elif args.subcommand == "transliterate":
        return cmd_transliterate(args)
    elif args.subcommand == "grammar":
        if args.grammar_cmd == "list":
            return cmd_grammar_list(args)
        elif args.grammar_cmd == "show":
            return cmd_grammar_show(args)
        elif args.grammar_cmd == "explain":
            return cmd_grammar_explain(args)
        elif args.grammar_cmd == "analyze":
            return cmd_grammar_analyze(args)
        else:
            parser.parse_args(["grammar", "--help"])
            return 0
    elif args.subcommand == "morphology":
        if args.morphology_cmd == "analyze":
            return cmd_morphology_analyze(args)
        elif args.morphology_cmd == "generate":
            return cmd_morphology_generate(args)
        elif args.morphology_cmd == "lemmatize":
            return cmd_morphology_lemmatize(args)
        else:
            parser.parse_args(["morphology", "--help"])
            return 0
    elif args.subcommand == "dialects":
        if args.dialects_cmd == "list":
            return cmd_dialects_list(args)
        elif args.dialects_cmd == "show":
            return cmd_dialects_show(args)
        elif args.dialects_cmd == "compare":
            return cmd_dialects_compare(args)
        else:
            parser.parse_args(["dialects", "--help"])
            return 0
    elif args.subcommand == "books":
        if args.books_cmd == "list":
            return cmd_books_list(args)
        elif args.books_cmd == "show":
            return cmd_books_show(args)
        elif args.books_cmd == "read":
            return cmd_books_read(args)
        elif args.books_cmd == "search":
            return cmd_books_search(args)
        else:
            parser.parse_args(["books", "--help"])
            return 0
    elif args.subcommand == "numbers":
        if args.numbers_cmd == "to-words":
            return cmd_numbers_to_words(args)
        elif args.numbers_cmd == "parse":
            return cmd_numbers_parse(args)
        elif args.numbers_cmd == "ordinal":
            return cmd_numbers_ordinal(args)
        else:
            parser.parse_args(["numbers", "--help"])
            return 0
    elif args.subcommand == "pronunciation":
        if args.pronunciation_cmd == "show":
            return cmd_pronunciation_show(args)
        else:
            parser.parse_args(["pronunciation", "--help"])
            return 0
    elif args.subcommand == "dataset":
        if args.dataset_cmd == "validate":
            return cmd_dataset_validate(args)
        elif args.dataset_cmd == "export":
            return cmd_dataset_export(args)
        elif args.dataset_cmd == "import":
            return cmd_dataset_import(args)
        else:
            parser.parse_args(["dataset", "--help"])
            return 0
    elif args.subcommand == "culture":
        if args.culture_cmd == "list":
            return cmd_culture_list(args)
        elif args.culture_cmd == "search":
            return cmd_culture_search(args)
        else:
            parser.parse_args(["culture", "--help"])
            return 0
    elif args.subcommand == "translate":
        return cmd_translate(args)
    elif args.subcommand == "db":
        if args.db_cmd == "build":
            return cmd_db_build(args)
        elif args.db_cmd == "import":
            return cmd_db_import(args)
        elif args.db_cmd == "stats":
            return cmd_db_stats(args)
        else:
            parser.parse_args(["db", "--help"])
            return 0
    elif args.subcommand == "stats":
        return cmd_stats(args)
    elif args.subcommand == "info":
        return cmd_info(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
