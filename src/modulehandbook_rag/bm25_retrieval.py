from __future__ import annotations

from rank_bm25 import BM25Okapi

from .preprocessing import tokenize_german
from .schemas import Chunk, SearchResult


def chunk_index_text(chunk: Chunk) -> str:
    """Text used for retrieval.

    Field chunks are short and may not repeat their module title. Adding
    metadata makes queries such as `WP3 Information Retrieval Prüfungsform`
    find the exact `Form der Modulprüfung` field instead of only the header.
    """

    module = " ".join(
        part for part in (chunk.module_code or "", chunk.module_title or "") if part
    )
    parts = [
        f"Dokument: {chunk.title}" if chunk.title else "",
        f"Modul: {module}" if module else "",
        f"Feld: {chunk.section}" if chunk.section else "",
        f"Inhalt: {chunk.text}",
    ]
    return "\n".join(p for p in parts if p)


def _contains_any(q: str, needles: tuple[str, ...]) -> bool:
    return any(needle in q for needle in needles)


def _field_intents(query: str) -> dict[str, bool]:
    """Detect handbook field intent in German, English, and Turkish queries.

    BM25 is still lexical, so dense/hybrid retrieval remains the recommended
    option for genuinely cross-lingual search. This multilingual intent layer
    helps query expansion and section boosting route English/Turkish questions
    to the German field labels used in LMU module handbooks.
    """

    q = " ".join(tokenize_german(query)).lower()
    return {
        "exam": _contains_any(q, (
            "prüf", "pruef", "klausur", "hausarbeit", "mündlich", "muendlich",
            "exam", "examination", "assessment", "test", "oral", "written",
            "sınav", "sinav", "değerlendirme", "degerlendirme", "ödev", "odev",
        )),
        "ects": _contains_any(q, (
            "ects", "punkte", "leistungspunkte", "credit", "credits",
            "akts", "kredi", "puan",
        )),
        "prerequisites": _contains_any(q, (
            "voraussetzung", "voraussetzungen", "prerequisite", "prerequisites",
            "requirement", "requirements", "ön koşul", "on kosul", "koşul", "kosul",
        )),
        "semester": _contains_any(q, (
            "semester", "empfohlen", "recommended", "study plan", "curriculum",
            "yarıyıl", "yariyil", "dönem", "donem", "önerilen", "onerilen",
        )),
        "responsible": _contains_any(q, (
            "verantwort", "dozent", "lecturer", "responsible", "coordinator",
            "teacher", "instructor", "sorumlu", "hoca", "öğretim", "ogretim",
        )),
        "language": _contains_any(q, (
            "sprache", "unterrichtssprache", "language", "teaching language",
            "instruction language", "dil", "öğretim dili", "ogretim dili",
        )),
        "content": _contains_any(q, (
            "inhalt", "inhalte", "behandelt", "themen", "covers", "cover",
            "content", "topic", "topics", "about", "konu", "içerik", "icerik", "ele al",
        )),
    }


def expand_query_tokens(query: str) -> list[str]:
    """Small domain-specific query expansion for module handbook fields."""

    tokens = tokenize_german(query)
    intents = _field_intents(query)
    extra: list[str] = []

    if intents["exam"]:
        extra += [
            "form",
            "modulprüfung",
            "modulprufung",
            "prüfung",
            "prufung",
            "klausur",
            "hausarbeit",
            "mündliche",
        ]
    if intents["ects"]:
        extra += ["ects", "punkte", "leistungspunkte", "modulteile"]
    if intents["prerequisites"]:
        extra += ["teilnahmevoraussetzung", "voraussetzung", "keine"]
    if intents["semester"]:
        extra += ["zeitpunkt", "studienverlauf", "empfohlenes", "semester"]
    if intents["responsible"]:
        extra += ["modulverantwortliche", "modulverantwortlicher", "verantwortlich"]
    if intents["language"]:
        extra += ["unterrichtssprache", "deutsch", "englisch"]
    if intents["content"]:
        extra += ["inhalte", "behandelt", "themen"]

    return tokens + tokenize_german(" ".join(extra))


def desired_sections_for_query(query: str) -> set[str]:
    intents = _field_intents(query)
    sections: set[str] = set()

    if intents["ects"]:
        sections.add("Zugeordnete Modulteile")
    if intents["exam"]:
        sections.add("Form der Modulprüfung")
    if intents["prerequisites"]:
        sections.add("Teilnahmevoraussetzung")
    if intents["semester"]:
        sections.add("Zeitpunkt im Studienverlauf")
    if intents["responsible"]:
        sections.add("Modulverantwortliche/r")
    if intents["language"]:
        sections.add("Unterrichtssprache")
    if intents["content"]:
        sections.add("Inhalte")

    return sections


class BM25Retriever:
    def __init__(
        self,
        chunks: list[Chunk],
        section_boost: float = 8.0,
        use_query_expansion: bool = True,
    ):
        if not chunks:
            raise ValueError("Cannot build retriever with zero chunks.")

        self.chunks = chunks
        self.section_boost = section_boost
        self.use_query_expansion = use_query_expansion
        self.tokenized = [tokenize_german(chunk_index_text(chunk)) for chunk in chunks]
        self.index = BM25Okapi(self.tokenized)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if self.use_query_expansion:
            query_tokens = expand_query_tokens(query)
        else:
            query_tokens = tokenize_german(query)

        scores = self.index.get_scores(query_tokens)
        desired_sections = desired_sections_for_query(query)

        boosted = []
        for i, score in enumerate(scores):
            section = self.chunks[i].section or ""
            boost = self.section_boost if section in desired_sections else 0.0
            boosted.append((i, float(score) + boost))

        ranked = sorted(boosted, key=lambda x: x[1], reverse=True)[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
