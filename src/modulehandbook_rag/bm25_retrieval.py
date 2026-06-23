from __future__ import annotations

from rank_bm25 import BM25Okapi

from .preprocessing import tokenize_german
from .schemas import Chunk, SearchResult


def chunk_index_text(chunk: Chunk) -> str:
    """Text used for retrieval.

    Field chunks are short and may not repeat their module title. Adding metadata
    makes queries like `WP3 Information Retrieval Prüfungsform` find the exact
    `Form der Modulprüfung` field instead of only the header.
    """
    parts = [
        chunk.module_code or "",
        chunk.module_title or "",
        chunk.section or "",
        chunk.text,
    ]
    return "\n".join(p for p in parts if p)


def expand_query_tokens(query: str) -> list[str]:
    """Small domain-specific query expansion for Modulhandbuch fields."""
    tokens = tokenize_german(query)
    q = " ".join(tokens)
    extra: list[str] = []
    if "prüf" in q or "pruef" in q or "klausur" in q or "hausarbeit" in q:
        extra += ["form", "modulprüfung", "modulprufung", "prüfung", "prufung", "klausur", "hausarbeit", "mündliche"]
    if "ects" in q or "punkte" in q:
        extra += ["ects", "punkte", "leistungspunkte", "modulteile"]
    if "voraussetzung" in q or "voraussetzungen" in q:
        extra += ["teilnahmevoraussetzung", "voraussetzung", "keine"]
    if "semester" in q or "empfohlen" in q:
        extra += ["zeitpunkt", "studienverlauf", "empfohlenes", "semester"]
    if "verantwort" in q or "dozent" in q:
        extra += ["modulverantwortliche", "modulverantwortlicher", "verantwortlich"]
    if "sprache" in q or "unterrichtssprache" in q:
        extra += ["unterrichtssprache", "deutsch", "englisch"]
    if "inhalt" in q or "inhalte" in q or "behandelt" in q or "themen" in q:
        extra += ["inhalte", "behandelt", "themen"]
    return tokens + tokenize_german(" ".join(extra))


def desired_sections_for_query(query: str) -> set[str]:
    q = " ".join(tokenize_german(query))
    sections: set[str] = set()
    if "ects" in q or "punkte" in q:
        sections.add("Zugeordnete Modulteile")
    if "prüf" in q or "pruef" in q or "klausur" in q or "hausarbeit" in q:
        sections.add("Form der Modulprüfung")
    if "voraussetzung" in q or "voraussetzungen" in q:
        sections.add("Teilnahmevoraussetzung")
    if "semester" in q or "empfohlen" in q:
        sections.add("Zeitpunkt im Studienverlauf")
    if "verantwort" in q or "dozent" in q:
        sections.add("Modulverantwortliche/r")
    if "sprache" in q or "unterrichtssprache" in q:
        sections.add("Unterrichtssprache")
    if "inhalt" in q or "inhalte" in q or "behandelt" in q or "themen" in q:
        sections.add("Inhalte")
    return sections


class BM25Retriever:
    def __init__(self, chunks: list[Chunk], section_boost: float = 0.0):
        if not chunks:
            raise ValueError("Cannot build retriever with zero chunks.")
        if section_boost < 0:
            raise ValueError("section_boost must be non-negative.")
        self.chunks = chunks
        self.section_boost = section_boost
        self.tokenized = [tokenize_german(chunk_index_text(chunk)) for chunk in chunks]
        self.index = BM25Okapi(self.tokenized)

    def scores(self, query: str) -> list[float]:
        """Return one deterministic score per corpus chunk.

        A zero boost is the reportable lexical baseline.  Any non-zero boost is
        an explicit, separately reported heuristic/ablation.
        """
        raw_scores = self.index.get_scores(expand_query_tokens(query))
        desired_sections = desired_sections_for_query(query)
        return [
            float(score) + (self.section_boost if (self.chunks[i].section or "") in desired_sections else 0.0)
            for i, score in enumerate(raw_scores)
        ]

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        scores = self.scores(query)
        ranked = sorted(enumerate(scores), key=lambda item: (-item[1], item[0]))[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
