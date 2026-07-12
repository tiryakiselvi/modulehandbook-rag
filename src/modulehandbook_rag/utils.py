from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
from .schemas import Chunk

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_jsonl(chunks: Iterable[Chunk], path: Path) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

def read_jsonl(path: Path | str) -> list[Chunk]:
    source = Path(path)
    chunks: list[Chunk] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                chunks.append(Chunk.from_dict(json.loads(line)))
    return chunks
