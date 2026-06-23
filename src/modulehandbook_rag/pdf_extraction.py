from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader

from .preprocessing import clean_text
from .schemas import Document


def extract_pdf_pages(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    docs: list[Document] = []
    title = path.stem
    for i, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        text = clean_text(raw)
        if not text:
            continue
        docs.append(
            Document(
                doc_id=f"{path.stem}:page:{i}",
                title=title,
                source_path=str(path),
                page_number=i,
                text=text,
            )
        )
    return docs
