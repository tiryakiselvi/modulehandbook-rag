from __future__ import annotations

import re

from .citations import format_source
from .bm25_retrieval import desired_sections_for_query
from .query_understanding import analyse_query
from .schemas import SearchResult

ABSTENTION_TEXT = "Diese Information ist im bereitgestellten Kontext nicht enthalten."
CLARIFICATION_TEXT = (
    "Bitte pr\u00e4zisieren Sie den Studiengang oder das Modulhandbuch, "
    "da derselbe Modulcode in mehreren Handb\u00fcchern vorkommt."
)


def answer_from_results(query: str, results: list[SearchResult]) -> str:
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."
    best = results[0].chunk
    text = re.sub(r"\s+", " ", best.text).strip()
    snippet = text[:1000] + (" ..." if len(text) > 1000 else "")
    return f"Antwort auf Basis der besten gefundenen Evidenz:\n\n{snippet}\n\nQuelle:\n- {format_source(best)}"


def build_context(results: list[SearchResult], max_chars: int = 7000) -> str:
    blocks: list[str] = []
    used = 0
    for result in results:
        text = re.sub(r"\s+", " ", result.chunk.text).strip()
        remaining = max_chars - used
        if remaining <= 0:
            break
        snippet = text[:remaining]
        blocks.append(f"[Quelle {result.rank}: {format_source(result.chunk)}]\n{snippet}")
        used += len(snippet)
    return "\n\n".join(blocks)


def build_rag_prompt(query: str, results: list[SearchResult]) -> str:
    return f"""Beantworte die Frage ausschlie\u00dflich mit den folgenden Modulhandbuchstellen.

Arbeitsregel:
- Pr\u00fcfe zuerst Quelle 1. Steht dort der verlangte Wert, Name oder Text ausdr\u00fccklich, gib ihn knapp wieder.
- Angaben direkt hinter Feldbezeichnungen wie ECTS, Modulverantwortliche/r, Unterrichtssprache oder Form der Modulpr\u00fcfung gelten als eindeutige Evidenz.
- Falls keine Quelle die verlangte Information ausdr\u00fccklich enth\u00e4lt, antworte exakt: \"{ABSTENTION_TEXT}\"
- Erfinde nichts und \u00fcbernimm Modulcodes, Zahlen, Namen und Pr\u00fcfungsformen unver\u00e4ndert.
- Antworte in derselben Sprache wie die Frage und nenne die verwendete Quelle.

Frage:
{query}

Kontext:
{build_context(results)}

Antwort:"""


def clarification_needed(query: str, results: list[SearchResult]) -> bool:
    """Detect module-code ambiguity across handbooks before generation."""

    if not results:
        return False
    analysis = analyse_query(query)
    if not analysis.has_module_code:
        return False
    if analysis.program or analysis.degree or analysis.variant:
        return False
    sources = {result.chunk.source_path for result in results if result.chunk.source_path}
    modules = {result.chunk.module_code for result in results if result.chunk.module_code}
    return len(sources) > 1 and len(modules) == 1


def structured_field_answer(query: str, results: list[SearchResult]) -> str | None:
    """Return exact field facts without asking the LLM to rewrite them."""

    unsupported_markers = (
        "datum", "wann findet", "uhrzeit", "raum", "e-mail", "email",
        "telefon", "note", "anmeldeschluss",
    )
    lowered = query.lower()
    if any(marker in lowered for marker in unsupported_markers):
        return None

    desired = desired_sections_for_query(query)
    exact_fields = {
        "Zugeordnete Modulteile",
        "Form der Modulpr\u00fcfung",
        "Teilnahmevoraussetzung",
        "Zeitpunkt im Studienverlauf",
        "Modulverantwortliche/r",
        "Unterrichtssprache",
    }
    candidates = [
        result
        for result in results
        if result.chunk.section in desired and result.chunk.section in exact_fields
    ]
    if not candidates:
        return None

    result = candidates[0]
    chunk = result.chunk
    text = re.sub(r"\s+", " ", chunk.text).strip()
    if chunk.section == "Zugeordnete Modulteile":
        match = re.search(r"insgesamt\s+([0-9]+(?:[.,][0-9]+)?)\s+ECTS-Punkte", text, re.IGNORECASE)
        if match:
            value = match.group(1)
            return f"{chunk.module_code} {chunk.module_title} umfasst {value} ECTS-Punkte. (Quelle {result.rank})"

    value = re.sub(rf"^{re.escape(chunk.section or '')}\s*", "", text, flags=re.IGNORECASE)
    if value:
        return f"{chunk.section}: {value} (Quelle {result.rank})"
    return None


def llm_answer_from_results(query: str, results: list[SearchResult], llm_generate) -> str:
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."
    if clarification_needed(query, results):
        return CLARIFICATION_TEXT
    structured_answer = structured_field_answer(query, results)
    if structured_answer:
        sources = "\n".join(f"- {format_source(result.chunk)}" for result in results)
        return f"{structured_answer}\n\nGefundene Quellen:\n{sources}"
    answer = llm_generate(build_rag_prompt(query, results)).strip()
    sources = "\n".join(f"- {format_source(result.chunk)}" for result in results)
    return f"{answer}\n\nGefundene Quellen:\n{sources}"
