from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader
from .preprocessing import clean_text
from .schemas import Document

def extract_pdf_pages(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    docs: list[Document] = []
    for index, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            docs.append(Document(
                doc_id=f"{path.stem}:page:{index}",
                title=path.stem,
                source_path=str(path),
                page_number=index,
                text=text,
            ))
    return docs
