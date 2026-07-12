from __future__ import annotations
from .schemas import Chunk, SearchResult

def format_source(chunk: Chunk) -> str:
    parts = [part for part in (
        chunk.module_code,
        chunk.module_title,
        f"Abschnitt: {chunk.section}" if chunk.section else None,
        f"Seite {chunk.page_number}" if chunk.page_number else None,
    ) if part]
    return " | ".join(parts) if parts else chunk.title

def format_result(result: SearchResult, snippet_chars: int = 500) -> str:
    snippet = result.chunk.text.replace("\n", " ")[:snippet_chars]
    if len(result.chunk.text) > snippet_chars:
        snippet += " …"
    return f"[{result.rank}] Score={result.score:.3f} | {format_source(result.chunk)}\n{snippet}"
