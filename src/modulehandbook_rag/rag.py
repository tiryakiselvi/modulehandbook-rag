from __future__ import annotations

import re

from .citations import format_source
from .schemas import SearchResult

KEY_FIELDS = [
    "ECTS",
    "Teilnahmevoraussetzung",
    "Zeitpunkt im Studienverlauf",
    "Dauer",
    "Inhalte",
    "Qualifikationsziele",
    "Form der Modulprüfung",
    "Form der Modulprufung",
    "Art der Bewertung",
    "Voraussetzung für die Vergabe",
    "Voraussetzung fur die Vergabe",
    "Modulverantwortliche/r",
    "Unterrichtssprache",
    "Sonstige Informationen",
]


def answer_from_results(query: str, results: list[SearchResult]) -> str:
    """Template-based answer that stays grounded in retrieved chunks.

    This is the local fallback before connecting a real LLM. It extracts common
    fields from Modulhandbuch chunks and cites only the chunk used for the answer.
    """
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."

    best = results[0].chunk
    extracted = _extract_likely_answer(query, best.text)
    if not extracted:
        extracted = _short_summary(best.text)

    lines = [
        "Antwort auf Basis der gefundenen Modulhandbuchstelle:",
        "",
        extracted,
        "",
        "Quelle:",
        f"- {format_source(best)}",
    ]
    return "\n".join(lines)


def build_context(results: list[SearchResult], max_chars: int = 6000) -> str:
    """Build a compact, cited context block for LLM-based RAG."""
    blocks: list[str] = []
    used = 0
    for result in results:
        chunk = result.chunk
        source = format_source(chunk)
        text = re.sub(r"\s+", " ", chunk.text).strip()
        remaining = max_chars - used
        if remaining <= 0:
            break
        snippet = text[: max(0, remaining)]
        block = f"[Quelle {result.rank}: {source}]\n{snippet}"
        blocks.append(block)
        used += len(snippet)
    return "\n\n".join(blocks)


def build_rag_prompt(query: str, results: list[SearchResult]) -> str:
    """Create a strict grounded-answer prompt for module-handbook RAG."""
    context = build_context(results)
    return f"""Du bist ein präziser Studiengangs-Assistent für universitäre Modulhandbücher.

Beantworte die Frage ausschließlich auf Basis des gegebenen Kontextes.
Wenn die Antwort im Kontext nicht enthalten ist, sage: "Diese Information wurde im bereitgestellten Modulhandbuch-Kontext nicht gefunden."
Erfinde keine Fakten.
Antworte auf Deutsch.

Wichtige Regeln:
- Gib Prüfungsformen, ECTS-Angaben, Voraussetzungen, Semesterangaben und Modulverantwortliche vollständig wieder.
- Wenn im Kontext mehrere Alternativen mit "oder" genannt werden, nenne alle Alternativen.
- Kürze offizielle Formulierungen nicht so, dass Informationen verloren gehen.
- Übernimm Zahlen, Zeitangaben und Klammerangaben genau aus dem Kontext.
- Nenne am Ende kurz die verwendeten Quellen in Klammern, z. B. (Quelle 1).

Frage:
{query}

Kontext:
{context}

Antwort:
"""

def llm_answer_from_results(query: str, results: list[SearchResult], llm_generate) -> str:
    """Generate a grounded RAG answer with an injected LLM generation function."""
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."
    prompt = build_rag_prompt(query, results)
    answer = llm_generate(prompt).strip()
    sources = "\n".join(f"- {format_source(result.chunk)}" for result in results)
    return "\n".join([answer, "", "Gefundene Quellen:", sources])


def _extract_likely_answer(query: str, text: str) -> str | None:
    q = query.lower()
    field_hints: list[str] = []

    if "ects" in q or "punkte" in q:
        ects_sentence = _extract_ects_sentence(text) or _sentence_containing(text, "ECTS-Punkte")
        if ects_sentence:
            return ects_sentence
        field_hints.append("ECTS")
    if "prüf" in q or "pruef" in q or "klausur" in q or "hausarbeit" in q:
        field_hints.extend(["Form der Modulprüfung", "Form der Modulprufung"])
    if "voraussetzung" in q:
        field_hints.append("Teilnahmevoraussetzung")
    if "semester" in q:
        field_hints.append("Zeitpunkt im Studienverlauf")
    if "verantwort" in q or "dozent" in q or "wer" in q and "modul" in q:
        field_hints.append("Modulverantwortliche/r")
    if "sprache" in q:
        field_hints.append("Unterrichtssprache")
    if "inhalt" in q or "behandelt" in q or "themen" in q:
        field_hints.append("Inhalte")

    for field in field_hints:
        value = _extract_field(text, field)
        if value:
            return f"{_canonical_field(field)}: {value}"

    query_terms = [t for t in re.findall(r"[a-zäöüß0-9]+", q) if len(t) > 4]
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    for sentence in sentences:
        lower = sentence.lower()
        if any(term in lower for term in query_terms):
            return re.sub(r"\s+", " ", sentence).strip()
    return None


def _extract_ects_sentence(text: str) -> str | None:
    match = re.search(r"Im Modul\s+.*?insgesamt\s+(\d+)\s+ECTS", text, re.IGNORECASE | re.DOTALL)
    if match:
        return f"Im Modul müssen insgesamt {match.group(1)} ECTS-Punkte erworben werden."
    return None


def _sentence_containing(text: str, term: str) -> str | None:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    for sentence in sentences:
        if term.lower() in sentence.lower():
            cleaned = re.sub(r"\s+", " ", sentence).strip()
            if len(cleaned) > 15:
                return cleaned[:900]
    return None


def _extract_field(text: str, field: str) -> str | None:
    labels = "|".join(re.escape(label) for label in KEY_FIELDS)
    pattern = re.compile(rf"{re.escape(field)}\s*(.*?)(?=\n(?:{labels})\b|$)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    value = re.sub(r"\s+", " ", match.group(1)).strip(" :-")
    return value[:900] if value else None


def _canonical_field(field: str) -> str:
    if field == "Form der Modulprufung":
        return "Form der Modulprüfung"
    return field


def _short_summary(text: str, max_chars: int = 900) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] + (" …" if len(text) > max_chars else "")
