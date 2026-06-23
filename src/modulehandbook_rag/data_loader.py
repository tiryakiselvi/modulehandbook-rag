from __future__ import annotations

from pathlib import Path

from .pdf_extraction import extract_pdf_pages
from .preprocessing import clean_text
from .schemas import Document


def load_documents(input_path: Path) -> list[Document]:
    """Load PDFs, TXT, and Markdown files from a file or directory."""
    paths: list[Path]
    if input_path.is_dir():
        paths = sorted(
            p for p in input_path.rglob("*")
            if p.suffix.lower() in {".pdf", ".txt", ".md"}
        )
    else:
        paths = [input_path]

    docs: list[Document] = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            docs.extend(extract_pdf_pages(path))
        elif suffix in {".txt", ".md"}:
            text = clean_text(path.read_text(encoding="utf-8"))
            docs.append(
                Document(
                    doc_id=path.stem,
                    title=path.stem,
                    source_path=str(path),
                    text=text,
                )
            )
    return docs
