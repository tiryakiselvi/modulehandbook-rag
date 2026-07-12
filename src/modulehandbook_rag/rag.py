from __future__ import annotations
import re
from .citations import format_source
from .schemas import SearchResult

def answer_from_results(query: str, results: list[SearchResult]) -> str:
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."
    best = results[0].chunk
    text = re.sub(r"\s+", " ", best.text).strip()
    snippet = text[:1000] + (" …" if len(text) > 1000 else "")
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
    return f"""Beantworte die Frage ausschließlich mit dem Kontext. Erfinde nichts.\n\nFrage: {query}\n\nKontext:\n{build_context(results)}\n\nAntwort:"""

def llm_answer_from_results(query: str, results: list[SearchResult], llm_generate) -> str:
    if not results:
        return "Ich habe keine passenden Stellen im Modulhandbuch gefunden."
    answer = llm_generate(build_rag_prompt(query, results)).strip()
    sources = "\n".join(f"- {format_source(result.chunk)}" for result in results)
    return f"{answer}\n\nGefundene Quellen:\n{sources}"
