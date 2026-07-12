from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryAnalysis:
    original_query: str
    language: str
    intents: tuple[str, ...]
    program: str | None
    degree: str | None
    variant: str | None
    has_module_code: bool
    bm25_query: str
    explanation: tuple[str, ...]


MODULE_CODE_RE = re.compile(r"\b(?:WP|P|M|BM|MA|CL|INF|CS)\s*[-.]?\s*\d+[A-Z]?\b", re.IGNORECASE)


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def _contains(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def detect_language(query: str, hint: str = "Auto") -> str:
    if hint in {"Deutsch", "English", "Türkçe"}:
        return hint

    q = _fold(query)
    original = query.lower()

    turkish_markers = (
        "hangi", "nedir", "ders", "sinav", "sınav", "ogretim", "öğretim",
        "bilgi erisimi", "bilgi erişimi", "arama motor", "kredi", "kosul", "koşul",
    )
    english_markers = (
        "which", "what", "where", "course", "exam", "credits",
        "prerequisite", "teaching language", "covers", "about", "responsible",
    )
    german_markers = (
        "welche", "welcher", "welches", "was", "wo", "veranstaltung",
        "behandelt", "gibt es", "gehoren", "gehören", "prufung", "prüfung",
        "studiengang", "nebenfach", "sommersemester", "wintersemester",
    )

    tr_score = sum(1 for marker in turkish_markers if marker in original or _fold(marker) in q)
    en_score = sum(1 for marker in english_markers if marker in q)
    de_score = sum(1 for marker in german_markers if _fold(marker) in q)

    if tr_score > 0:
        return "Türkçe"
    if en_score > de_score and en_score > 0:
        return "English"
    return "Deutsch"


def analyse_query(query: str, language_hint: str = "Auto") -> QueryAnalysis:
    q = _fold(query)
    language = detect_language(query, language_hint)
    intents: list[str] = []
    additions: list[str] = []
    explanation: list[str] = []

    intent_rules: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
        "Prüfungsform": (
            ("pruf", "klausur", "hausarbeit", "exam", "assessment", "test", "sinav", "odev"),
            ("Form der Modulprüfung", "Prüfung", "Klausur", "Hausarbeit"),
        ),
        "ECTS": (
            ("ects", "leistungspunkt", "credit", "credits", "akts", "kredi", "puan"),
            ("ECTS", "Leistungspunkte"),
        ),
        "Voraussetzungen": (
            ("voraussetzung", "prerequisite", "requirement", "on kosul", "kosul"),
            ("Teilnahmevoraussetzung", "Voraussetzungen"),
        ),
        "Studienverlauf": (
            ("semester", "studienverlauf", "recommended", "curriculum", "yariyil", "donem"),
            ("Zeitpunkt im Studienverlauf", "Semester"),
        ),
        "Verantwortliche": (
            ("verantwort", "dozent", "lecturer", "responsible", "coordinator", "sorumlu", "hoca"),
            ("Modulverantwortliche", "Dozent"),
        ),
        "Unterrichtssprache": (
            ("unterrichtssprache", "teaching language", "instruction language", "ogretim dili", "dil"),
            ("Unterrichtssprache", "Deutsch", "Englisch"),
        ),
        "Inhalte": (
            ("inhalt", "behandelt", "thema", "covers", "about", "content", "topic", "konu", "icerik", "ele al"),
            ("Inhalte", "Themen", "behandelt"),
        ),
    }

    for intent, (markers, german_terms) in intent_rules.items():
        if _contains(q, markers):
            intents.append(intent)
            additions.extend(german_terms)

    concept_rules: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
        "Information Retrieval": (
            ("information retrieval", "bilgi erisimi", "informationsretrieval"),
            ("Information Retrieval", "Informationssuche", "Suchmaschinen"),
        ),
        "Suchmaschinen": (
            ("suchmaschine", "search engine", "arama motor"),
            ("Suchmaschinen", "Information Retrieval", "Websuche"),
        ),
        "Sprachverarbeitung": (
            ("sprachverarbeitung", "natural language processing", "nlp", "dogal dil isleme"),
            ("Sprachverarbeitung", "Computerlinguistik", "Natural Language Processing"),
        ),
        "Maschinelles Lernen": (
            ("maschinelles lernen", "machine learning", "makine ogrenmesi"),
            ("Maschinelles Lernen", "Machine Learning"),
        ),
        "Datenbanken": (
            ("datenbank", "database", "veri taban"),
            ("Datenbanken", "Datenbanksysteme"),
        ),
    }

    detected_concepts: list[str] = []
    for concept, (markers, german_terms) in concept_rules.items():
        if _contains(q, markers):
            detected_concepts.append(concept)
            additions.extend(german_terms)

    program: str | None = None
    if _contains(q, ("computerlinguistik", "computational linguistics", "hesaplamali dilbilim")):
        program = "Computerlinguistik"
    elif _contains(q, ("informatik", "computer science", "bilgisayar bilimi")):
        program = "Informatik"

    degree: str | None = None
    if "bachelor" in q:
        degree = "Bachelor"
    elif "master" in q:
        degree = "Master"

    variant: str | None = None
    if _contains(q, ("30 ects", "30 akts")):
        variant = "Nebenfach 30 ECTS"
    elif _contains(q, ("60 ects", "60 akts")):
        variant = "Nebenfach 60 ECTS"
    elif _contains(q, ("nebenfach", "minor", "yan dal")):
        variant = "Nebenfach"
    elif _contains(q, ("sommersemester", "sose", "summer semester", "yaz donemi")):
        variant = "SoSe"
    elif _contains(q, ("wintersemester", "wise", "winter semester", "kis donemi")):
        variant = "WiSe"

    has_module_code = bool(MODULE_CODE_RE.search(query))

    if language != "Deutsch":
        explanation.append(f"Fragesprache erkannt: {language}")
        additions.extend(("Modul", "Modulhandbuch"))
    if intents:
        explanation.append("Intent: " + ", ".join(intents))
    if detected_concepts:
        explanation.append("Thema: " + ", ".join(detected_concepts))
    if program:
        explanation.append("Studiengang: " + program)
    if degree:
        explanation.append("Abschluss: " + degree)
    if variant:
        explanation.append("Variante: " + variant)
    if has_module_code:
        explanation.append("Explizite Modulnummer erkannt")
    else:
        explanation.append("Keine Modulnummer nötig, semantische Suche wird genutzt")

    # Preserve order while removing duplicates.
    unique_additions = list(dict.fromkeys(term for term in additions if term))
    bm25_query = " ".join([query, *unique_additions]).strip()

    return QueryAnalysis(
        original_query=query,
        language=language,
        intents=tuple(intents),
        program=program,
        degree=degree,
        variant=variant,
        has_module_code=has_module_code,
        bm25_query=bm25_query,
        explanation=tuple(explanation),
    )


def recommended_retriever(analysis: QueryAnalysis) -> str:
    """Choose a robust default without hiding the actual selected retriever."""

    if analysis.language != "Deutsch":
        return "Hybrid"
    if analysis.has_module_code:
        return "BM25"
    return "Hybrid"
