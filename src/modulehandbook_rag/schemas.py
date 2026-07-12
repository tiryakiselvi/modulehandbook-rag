from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Document:
    doc_id: str
    title: str
    source_path: str
    text: str
    page_number: int | None = None

@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source_path: str
    text: str
    page_number: int | None = None
    module_code: str | None = None
    module_title: str | None = None
    section: str | None = None
    document_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Chunk":
        allowed = {field.name for field in __import__('dataclasses').fields(Chunk)}
        return Chunk(**{key: value for key, value in data.items() if key in allowed})

@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    rank: int
