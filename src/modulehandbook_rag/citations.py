from __future__ import annotations

from .schemas import Chunk, SearchResult


def format_source(chunk: Chunk) -> str:
    parts = []
    if chunk.module_code:
        parts.append(chunk.module_code)
    if chunk.module_title:
        parts.append(chunk.module_title)
    if chunk.section:
        parts.append(f"Abschnitt: {chunk.section}")
    if chunk.page_number:
        parts.append(f"Seite {chunk.page_number}")
    return " | ".join(parts) if parts else chunk.title


def format_result(result: SearchResult, snippet_chars: int = 500) -> str:
    chunk = result.chunk
    snippet = chunk.text.replace("\n", " ")[:snippet_chars]
    if len(chunk.text) > snippet_chars:
        snippet += " …"
    return f"[{result.rank}] Score={result.score:.3f} | {format_source(chunk)}\n{snippet}"
