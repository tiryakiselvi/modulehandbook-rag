from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .schemas import Chunk, Document

# Covers the current P/WP handbook and common Master codes (e.g. M1, MP3).
# A heading is still validated by its repeated module fields below, so TOC hits
# are excluded.
MODULE_RE = re.compile(r"Modul:\s+([A-Z]{1,4}\d+[A-Z]?)\s+([^\n]+)", re.IGNORECASE)
SECTION_LABELS = [
    "Englischer Modultitel",
    "Zuordnung zum Studiengang",
    "Zugeordnete Modulteile",
    "Art des Moduls",
    "Verwendbarkeit des Moduls",
    "Wahlpflichtregelungen",
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


def naive_chunks(docs: list[Document], chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        text = doc.text
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc.doc_id}:chunk:{idx}",
                        doc_id=doc.doc_id,
                        title=doc.title,
                        source_path=doc.source_path,
                        page_number=doc.page_number,
                        text=chunk_text,
                        section="naive",
                    )
                )
            if end == len(text):
                break
            start = max(0, end - overlap)
            idx += 1
    return chunks


def module_chunks(docs: list[Document]) -> list[Chunk]:
    """Create one chunk per detected module by joining consecutive pages."""
    by_source: dict[str, list[Document]] = defaultdict(list)
    for doc in docs:
        by_source[doc.source_path].append(doc)

    chunks: list[Chunk] = []
    for source_path, pages in by_source.items():
        pages = sorted(pages, key=lambda d: d.page_number or 0)
        full_text_parts: list[tuple[int | None, str]] = [(p.page_number, p.text) for p in pages]
        full_text = "\n\n".join(text for _, text in full_text_parts)

        matches = list(MODULE_RE.finditer(full_text))
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
            module_text = full_text[start:end].strip()
            # Skip table-of-contents entries that look like module headings but do not contain a real module page.
            if "Englischer Modultitel" not in module_text and "Zugeordnete Modulteile" not in module_text:
                continue
            code = match.group(1).strip().upper()
            title = re.sub(r"\s*\.+\s*\d+\s*$", "", match.group(2).strip())
            page_number = _guess_page_number(full_text_parts, start)
            chunks.append(
                Chunk(
                    chunk_id=f"{source_path}:module:{code}",
                    doc_id=source_path,
                    title=Path(source_path).name,
                    source_path=source_path,
                    page_number=page_number,
                    module_code=code,
                    module_title=title,
                    section="module",
                    text=module_text,
                )
            )
    return chunks


def field_chunks(docs: list[Document]) -> list[Chunk]:
    """Split module chunks into field chunks such as `Inhalte` or `Form der Modulprüfung`.

    Modulhandbücher are semi-structured documents. Field chunks are usually better
    for precise questions like ECTS, exam type, responsible lecturer, or recommended
    semester because the retriever can return the exact field instead of an entire module.
    """
    modules = module_chunks(docs)
    chunks: list[Chunk] = []
    label_pattern = "|".join(re.escape(label) for label in SECTION_LABELS)
    section_re = re.compile(rf"\b({label_pattern})\b", re.IGNORECASE)

    for module in modules:
        matches = list(section_re.finditer(module.text))
        if not matches:
            chunks.append(module)
            continue
        header = module.text[: matches[0].start()].strip()
        if header:
            chunks.append(_copy_chunk(module, f"{module.chunk_id}:header", header, "header"))
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(module.text)
            section_name = _canonical_section_name(match.group(1))
            section_text = module.text[start:end].strip()
            if len(section_text) > 20:
                section_slug = re.sub(r"\W+", "_", section_name.lower()).strip("_")
                chunks.append(
                    _copy_chunk(
                        module,
                        f"{module.chunk_id}:field:{section_slug}",
                        section_text,
                        section_name,
                    )
                )
    return chunks


def make_chunks(docs: list[Document], mode: str, chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    if mode == "naive":
        return naive_chunks(docs, chunk_size=chunk_size, overlap=overlap)
    if mode == "module":
        return module_chunks(docs)
    if mode == "field":
        return field_chunks(docs)
    raise ValueError(f"Unknown chunking mode: {mode}")


def _canonical_section_name(section: str) -> str:
    section = section.strip()
    if section.lower() == "form der modulprufung":
        return "Form der Modulprüfung"
    if section.lower() == "voraussetzung fur die vergabe":
        return "Voraussetzung für die Vergabe"
    return section


def _copy_chunk(base: Chunk, chunk_id: str, text: str, section: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=base.doc_id,
        title=base.title,
        source_path=base.source_path,
        page_number=base.page_number,
        module_code=base.module_code,
        module_title=base.module_title,
        section=section,
        text=text,
    )


def _guess_page_number(parts: list[tuple[int | None, str]], char_offset: int) -> int | None:
    seen = 0
    for page_number, text in parts:
        seen += len(text) + 2
        if char_offset <= seen:
            return page_number
    return parts[-1][0] if parts else None
