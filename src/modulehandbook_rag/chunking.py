from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .schemas import Chunk, Document

# Supports P1, WP3, M1 and layouts with a space in the code (e.g. "WP 1").
# Headings are validated against repeated module fields below so that TOC entries
# do not become module chunks.
MODULE_RE = re.compile(
    r"(?im)^\s*Modul:\s+([A-Z]{1,4}\s*\d+[A-Z]?|[A-Z]{2,})\s+([^\n]+)"
)
LEGAL_SECTION_RE = re.compile(r"(?im)^\s*§\s*(\d+[a-z]?)\s*(?:\n\s*)?([^\n]+)")

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
    """Create fixed-size baseline chunks for every page of every input document."""
    chunks: list[Chunk] = []
    for doc in docs:
        text = doc.text
        start = 0
        idx = 0
        document_type = _infer_document_type(text)
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
                        document_type=document_type,
                    )
                )
            if end == len(text):
                break
            start = max(0, end - overlap)
            idx += 1
    return chunks


def module_chunks(docs: list[Document]) -> list[Chunk]:
    """Create module chunks, with one document chunk as a safe fallback.

    Regulations and study plans do not use ``Modul:`` headings.  Keeping a
    fallback chunk prevents those documents from silently disappearing from a
    multi-document corpus.
    """
    chunks: list[Chunk] = []
    for source_path, pages in _group_by_source(docs).items():
        full_text_parts, full_text = _join_pages(pages)
        document_type = _infer_document_type(full_text)
        matches = list(MODULE_RE.finditer(full_text))
        source_chunks: list[Chunk] = []

        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
            module_text = full_text[start:end].strip()
            if not _looks_like_module_record(module_text):
                continue
            code = re.sub(r"\s+", "", match.group(1)).upper()
            module_title = re.sub(r"\s*\.+\s*\d+\s*$", "", match.group(2).strip())
            source_chunks.append(
                Chunk(
                    chunk_id=f"{source_path}:module:{code}",
                    doc_id=source_path,
                    title=Path(source_path).name,
                    source_path=source_path,
                    page_number=_guess_page_number(full_text_parts, start),
                    module_code=code,
                    module_title=module_title,
                    section="module",
                    text=module_text,
                    document_type=document_type,
                )
            )

        chunks.extend(source_chunks or [_document_chunk(source_path, full_text_parts, full_text, document_type)])
    return chunks


def field_chunks(docs: list[Document]) -> list[Chunk]:
    """Create field chunks for handbooks and section chunks for regulations.

    This is the structure-aware strategy for heterogeneous academic documents:
    module handbook fields, legal ``§`` sections, and a document fallback for
    short plans or admission notes.
    """
    chunks: list[Chunk] = []
    label_pattern = "|".join(re.escape(label) for label in SECTION_LABELS)
    field_re = re.compile(rf"\b({label_pattern})\b", re.IGNORECASE)

    for base in module_chunks(docs):
        if base.document_type != "module_handbook":
            legal_chunks = _legal_section_chunks(base)
            chunks.extend(legal_chunks or [base])
            continue

        matches = list(field_re.finditer(base.text))
        if not matches:
            chunks.append(base)
            continue
        header = base.text[: matches[0].start()].strip()
        if header:
            chunks.append(_copy_chunk(base, f"{base.chunk_id}:header", header, "header"))
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(base.text)
            section_name = _canonical_section_name(match.group(1))
            section_text = base.text[start:end].strip()
            if len(section_text) > 20:
                section_slug = re.sub(r"\W+", "_", section_name.lower()).strip("_")
                chunks.append(_copy_chunk(base, f"{base.chunk_id}:field:{section_slug}", section_text, section_name))
    return chunks


def make_chunks(docs: list[Document], mode: str, chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    if mode == "naive":
        chunks = naive_chunks(docs, chunk_size=chunk_size, overlap=overlap)
    elif mode == "module":
        chunks = module_chunks(docs)
    elif mode == "field":
        chunks = field_chunks(docs)
    else:
        raise ValueError(f"Unknown chunking mode: {mode}")
    return _deduplicate_chunks(chunks)


def _group_by_source(docs: list[Document]) -> dict[str, list[Document]]:
    by_source: dict[str, list[Document]] = defaultdict(list)
    for doc in docs:
        by_source[doc.source_path].append(doc)
    return by_source


def _deduplicate_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Keep one deterministic representative for each logical chunk id.

    PDF extraction can repeat a module heading in a footer or reconstructed
    table of contents. Repeated ids would otherwise waste result slots and can
    inflate ranking metrics.
    """
    unique: dict[str, Chunk] = {}
    for chunk in chunks:
        current = unique.get(chunk.chunk_id)
        if current is None or len(chunk.text) > len(current.text):
            unique[chunk.chunk_id] = chunk
    return list(unique.values())


def _join_pages(pages: list[Document]) -> tuple[list[tuple[int | None, str]], str]:
    ordered = sorted(pages, key=lambda doc: doc.page_number or 0)
    parts = [(page.page_number, page.text) for page in ordered]
    return parts, "\n\n".join(text for _, text in parts)


def _document_chunk(
    source_path: str,
    parts: list[tuple[int | None, str]],
    text: str,
    document_type: str,
) -> Chunk:
    return Chunk(
        chunk_id=f"{source_path}:document",
        doc_id=source_path,
        title=Path(source_path).name,
        source_path=source_path,
        page_number=parts[0][0] if parts else None,
        section="document",
        text=text,
        document_type=document_type,
    )


def _legal_section_chunks(base: Chunk) -> list[Chunk]:
    matches = list(LEGAL_SECTION_RE.finditer(base.text))
    chunks: list[Chunk] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(base.text)
        section_text = base.text[start:end].strip()
        if len(section_text) < 50:
            continue
        number = match.group(1)
        heading = re.sub(r"\s+", " ", match.group(2)).strip()
        # References such as "§ 11 Abs. 5 gilt ..." are not section headings.
        if re.match(r"^(abs\.|satz|nr\.|gilt\b|wird\b|ist\b|sind\b)", heading, re.IGNORECASE):
            continue
        section = f"§ {number}" + (f" {heading}" if heading else "")
        slug = re.sub(r"\W+", "_", number).strip("_")
        chunks.append(_copy_chunk(base, f"{base.chunk_id}:legal:{slug}:{idx}", section_text, section))
    return chunks


def _looks_like_module_record(text: str) -> bool:
    field_markers = (
        "Englischer Modultitel",
        "Zugeordnete Modulteile",
        "Verwendbarkeit des Moduls",
        "Qualifikationsziele",
        "Modulverantwortliche",
        "Unterrichtssprache",
    )
    return len(text) > 400 and any(marker.lower() in text.lower() for marker in field_markers)


def _infer_document_type(text: str) -> str:
    lowered = text[:5000].lower()
    if "modulhandbuch" in lowered:
        return "module_handbook"
    if "prüfungs- und studienordnung" in lowered or "pruefungs- und studienordnung" in lowered:
        return "examination_regulations"
    if "bewerbung" in lowered:
        return "admission_information"
    if "studienplan" in lowered or "studienablauf" in lowered:
        return "study_plan"
    if "satzung" in lowered or "eignungsverfahren" in lowered:
        return "statute"
    return "other"


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
        document_type=base.document_type,
    )


def _guess_page_number(parts: list[tuple[int | None, str]], char_offset: int) -> int | None:
    seen = 0
    for page_number, text in parts:
        seen += len(text) + 2
        if char_offset <= seen:
            return page_number
    return parts[-1][0] if parts else None
