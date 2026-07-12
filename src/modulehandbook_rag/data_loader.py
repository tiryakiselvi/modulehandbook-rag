from __future__ import annotations
from pathlib import Path
from .pdf_extraction import extract_pdf_pages
from .preprocessing import clean_text
from .schemas import Document

def load_documents(input_path: Path) -> list[Document]:
    paths = sorted(
        path for path in input_path.rglob("*")
        if path.suffix.lower() in {".pdf", ".txt", ".md"}
    ) if input_path.is_dir() else [input_path]
    docs: list[Document] = []
    for path in paths:
        if path.suffix.lower() == ".pdf":
            docs.extend(extract_pdf_pages(path))
        elif path.suffix.lower() in {".txt", ".md"}:
            docs.append(Document(
                doc_id=path.stem,
                title=path.stem,
                source_path=str(path),
                text=clean_text(path.read_text(encoding="utf-8")),
            ))
    return docs
