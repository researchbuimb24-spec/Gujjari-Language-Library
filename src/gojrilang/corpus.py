"""Corpus analytics and concordance exploration subsystem for Gojri.

Provides full-corpus statistics (tokens, types, sentences, type-token ratio,
hapax legomena, frequency distribution) and Key-Word-In-Context (KWIC)
concordances across Gojri literature, epics, songs, and folktales.
"""

from __future__ import annotations

import collections
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from gojrilang.books import list_books, get_book
from gojrilang.epics import list_epics, get_epic
from gojrilang.nlp import sent_tokenize, tokenize
from gojrilang.normalize import normalize_for_search
from gojrilang.songs import list_songs


@dataclass
class CorpusStatistics:
    """Quantitative linguistic metrics of a Gojri text corpus."""

    total_documents: int
    total_sentences: int
    total_tokens: int
    total_unique_types: int
    type_token_ratio: float
    hapax_legomena_count: int  # Words occurring exactly once
    top_words: List[Tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Corpus:
    """An analytical text corpus of Gojri linguistic materials."""

    def __init__(self, name: str = "Gojri Literature & Oral Corpus") -> None:
        self.name = name
        self.documents: List[Dict[str, Any]] = []
        self._tokens: List[str] = []
        self._sentences: List[str] = []
        self._freq: Optional[collections.Counter] = None

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a raw text document to the corpus."""
        doc = {
            "doc_id": doc_id,
            "text": text,
            "metadata": metadata or {},
        }
        self.documents.append(doc)
        # Tokenize and segment sentences
        sents = sent_tokenize(text)
        self._sentences.extend(sents)
        toks = tokenize(text, preserve_punctuation=False)
        self._tokens.extend(toks)
        self._freq = None  # Invalidate frequency cache

    @classmethod
    def load_built_in_corpus(cls) -> Corpus:
        """Load all texts from packaged literature books, epics, and songs into a unified corpus."""
        c = cls(name="Gojri Core Preserved Corpus")

        # Ingest books
        for meta in list_books():
            book = get_book(meta.id)
            for page in book.pages:
                c.add_document(
                    doc_id=f"book_{book.id}_p{page.page_number}",
                    text=page.get_text("perso-arabic"),
                    metadata={"source": "book", "book_id": book.id, "title": book.title},
                )

        # Ingest epics
        for epic_meta in list_epics():
            epic = get_epic(epic_meta["id"])
            for section in epic.sections:
                for chap in section.chapters:
                    chap_text = " ".join(v.text_perso_arabic for v in chap.verses)
                    c.add_document(
                        doc_id=f"epic_{epic.id}_{section.id}_c{chap.chapter_num}",
                        text=chap_text,
                        metadata={"source": "epic", "epic_id": epic.id, "chapter": chap.title},
                    )

        # Ingest songs
        for song in list_songs():
            song_text = " ".join(v.text_perso_arabic for v in song.verses)
            c.add_document(
                doc_id=f"song_{song.id}",
                text=song_text,
                metadata={"source": "song", "title": song.title, "category": song.category},
            )

        return c

    def get_statistics(self) -> CorpusStatistics:
        """Compute full corpus statistics."""
        if self._freq is None:
            self._freq = collections.Counter(normalize_for_search(t) for t in self._tokens if t)

        total_tokens = len(self._tokens)
        unique_types = len(self._freq)
        ttr = (unique_types / total_tokens) if total_tokens > 0 else 0.0
        hapax = sum(1 for _, count in self._freq.items() if count == 1)
        top = self._freq.most_common(20)

        return CorpusStatistics(
            total_documents=len(self.documents),
            total_sentences=len(self._sentences),
            total_tokens=total_tokens,
            total_unique_types=unique_types,
            type_token_ratio=round(ttr, 4),
            hapax_legomena_count=hapax,
            top_words=top,
        )

    def concordance(self, word: str, window: int = 4) -> List[Dict[str, Any]]:
        """Return Key-Word-In-Context (KWIC) concordance lines for a target word."""
        q_norm = normalize_for_search(word)
        results: List[Dict[str, Any]] = []

        for doc in self.documents:
            tokens = tokenize(doc["text"], preserve_punctuation=False)
            for idx, tok in enumerate(tokens):
                if normalize_for_search(tok) == q_norm:
                    left = tokens[max(0, idx - window) : idx]
                    right = tokens[idx + 1 : min(len(tokens), idx + window + 1)]
                    results.append({
                        "doc_id": doc["doc_id"],
                        "left": left,
                        "left_context": " ".join(left),
                        "keyword": tok,
                        "right": right,
                        "right_context": " ".join(right),
                    })
        return results


_DEFAULT_CORPUS: Optional[Corpus] = None


def get_corpus() -> Corpus:
    """Get or initialize the shared built-in Gojri corpus."""
    global _DEFAULT_CORPUS
    if _DEFAULT_CORPUS is None:
        _DEFAULT_CORPUS = Corpus.load_built_in_corpus()
    return _DEFAULT_CORPUS


def get_corpus_statistics() -> CorpusStatistics:
    """Convenience helper to compute statistics for the built-in Gojri corpus."""
    return get_corpus().get_statistics()


def concordance(word: str, window: int = 4) -> List[Dict[str, Any]]:
    """Convenience helper to search KWIC concordance in the built-in Gojri corpus."""
    return get_corpus().concordance(word=word, window=window)
