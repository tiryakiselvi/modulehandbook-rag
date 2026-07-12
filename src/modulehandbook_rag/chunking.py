from __future__ import annotations
import re
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from .handbook_config import DEFAULT_MODULE_PATTERN, DEFAULT_SECTION_LABELS
from .schemas import Chunk, Document

def _group(docs: list[Document]) -> dict[str, list[Document]]:
    grouped: dict[str, list[Document]] = defaultdict(list)
    for doc in docs:
        grouped[doc.source_path].append(doc)
    return grouped

def _joined(pages: list[Document]) -> tuple[list[tuple[int | None, str]], str]:
    ordered = sorted(pages, key=lambda item: item.page_number or 0)
    parts = [(item.page_number, item.text) for item in ordered]
    return parts, "\n\n".join(text for _, text in parts)

def _page(parts: list[tuple[int | None, str]], offset: int) -> int | None:
    seen = 0
    for page_number, text in parts:
        seen += len(text) + 2
        if offset <= seen:
            return page_number
    return parts[-1][0] if parts else None

def _module_matches(text: str, pattern: str):
    regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    return regex, list(regex.finditer(text))

def naive_chunks(docs: list[Document], chunk_size: int = 900, overlap: int = 120,
                 module_pattern: str = DEFAULT_MODULE_PATTERN) -> list[Chunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    chunks: list[Chunk] = []
    for source, pages in _group(docs).items():
        parts, text = _joined(pages)
        _, matches = _module_matches(text, module_pattern)
        start = index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            body = text[start:end].strip()
            code = title = None
            preceding = [match for match in matches if match.start() <= start]
            if preceding:
                match = preceding[-1]
                code = re.sub(r"\s+", "", match.group(1)).upper()
                title = re.sub(r"\s*\.+\s*\d+\s*$", "", match.group(2).strip())
            if body:
                chunks.append(Chunk(
                    chunk_id=f"{source}:naive:{index}", doc_id=source,
                    title=Path(source).name, source_path=source, text=body,
                    page_number=_page(parts, start), module_code=code,
                    module_title=title, section="naive",
                ))
            if end >= len(text):
                break
            start = end - overlap
            index += 1
    return chunks

def module_chunks(docs: list[Document], module_pattern: str = DEFAULT_MODULE_PATTERN) -> list[Chunk]:
    chunks: list[Chunk] = []
    for source, pages in _group(docs).items():
        parts, text = _joined(pages)
        _, matches = _module_matches(text, module_pattern)
        source_chunks: list[Chunk] = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.start():end].strip()
            if len(body) < 200:
                continue
            code = re.sub(r"\s+", "", match.group(1)).upper()
            title = re.sub(r"\s*\.+\s*\d+\s*$", "", match.group(2).strip())
            source_chunks.append(Chunk(
                chunk_id=f"{source}:module:{code}", doc_id=source,
                title=Path(source).name, source_path=source, text=body,
                page_number=_page(parts, match.start()), module_code=code,
                module_title=title, section="module", document_type="module_handbook",
            ))
        if source_chunks:
            chunks.extend(source_chunks)
        elif text.strip():
            chunks.append(Chunk(
                chunk_id=f"{source}:document", doc_id=source,
                title=Path(source).name, source_path=source, text=text.strip(),
                page_number=parts[0][0] if parts else None, section="document",
            ))
    return chunks

def field_chunks(docs: list[Document], module_pattern: str = DEFAULT_MODULE_PATTERN,
                 section_labels: Sequence[str] = DEFAULT_SECTION_LABELS) -> list[Chunk]:
    labels = "|".join(re.escape(label) for label in section_labels)
    regex = re.compile(rf"(?im)^\s*({labels})\s*$|\b({labels})\b")
    chunks: list[Chunk] = []
    for module in module_chunks(docs, module_pattern):
        if not module.module_code:
            chunks.append(module)
            continue
        matches = list(regex.finditer(module.text))
        if not matches:
            chunks.append(module)
            continue
        header = module.text[:matches[0].start()].strip()
        if header:
            chunks.append(_copy(module, f"{module.chunk_id}:header", header, "header"))
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(module.text)
            name = next(group for group in match.groups() if group)
            if name.lower() == "form der modulprufung":
                name = "Form der Modulprüfung"
            body = module.text[start:end].strip()
            if len(body) > 20:
                slug = re.sub(r"\W+", "_", name.lower()).strip("_")
                chunks.append(_copy(module, f"{module.chunk_id}:field:{slug}", body, name))
    return _dedupe(chunks)

def _copy(base: Chunk, chunk_id: str, text: str, section: str) -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id=base.doc_id, title=base.title,
                 source_path=base.source_path, text=text, page_number=base.page_number,
                 module_code=base.module_code, module_title=base.module_title,
                 section=section, document_type=base.document_type)

def _dedupe(chunks: list[Chunk]) -> list[Chunk]:
    unique: dict[str, Chunk] = {}
    for chunk in chunks:
        if chunk.chunk_id not in unique or len(chunk.text) > len(unique[chunk.chunk_id].text):
            unique[chunk.chunk_id] = chunk
    return list(unique.values())

def make_chunks(docs: list[Document], mode: str, chunk_size: int = 900, overlap: int = 120,
                module_pattern: str = DEFAULT_MODULE_PATTERN,
                section_labels: Sequence[str] = DEFAULT_SECTION_LABELS) -> list[Chunk]:
    if mode == "naive":
        return naive_chunks(docs, chunk_size, overlap, module_pattern)
    if mode == "module":
        return module_chunks(docs, module_pattern)
    if mode == "field":
        return field_chunks(docs, module_pattern, section_labels)
    raise ValueError(f"Unknown chunking mode: {mode}")
