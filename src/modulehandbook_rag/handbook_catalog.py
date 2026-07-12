from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .query_understanding import QueryAnalysis


@dataclass(frozen=True)
class HandbookOption:
    key: str
    label: str
    program: str
    degree: str
    variant: str
    filename: str
    recommended: bool = False
    note: str = ""


HANDBOOKS: list[HandbookOption] = [
    HandbookOption(
        key="cl_bsc",
        label="Computerlinguistik · Bachelor",
        program="Computerlinguistik",
        degree="Bachelor",
        variant="Hauptfach, 120 ECTS",
        filename="lmu_computerlinguistik_bsc_stand_2025-09-24.pdf",
        recommended=True,
        note="Standard für Bachelor-Fragen zur Computerlinguistik.",
    ),
    HandbookOption(
        key="cl_msc",
        label="Computerlinguistik · Master",
        program="Computerlinguistik",
        degree="Master",
        variant="Master mit Profilbereich, 120 ECTS",
        filename="lmu_computerlinguistik_msc_stand_2025-07-08.pdf",
        recommended=True,
        note="Standard für Master-Fragen zur Computerlinguistik.",
    ),
    HandbookOption(
        key="inf_bsc_integrated",
        label="Informatik · Bachelor · integriertes Anwendungsfach",
        program="Informatik",
        degree="Bachelor",
        variant="Integriertes Anwendungsfach",
        filename="lmu_informatik_bsc_integriertes_anwendungsfach_stand_2023-11-22.pdf",
        recommended=True,
        note="Standard für Informatik-Bachelor-Fragen, sofern kein Nebenfach genannt wird.",
    ),
    HandbookOption(
        key="inf_bsc_minor_60",
        label="Informatik · Bachelor · Nebenfach 60 ECTS",
        program="Informatik",
        degree="Bachelor",
        variant="Nebenfach 60 ECTS",
        filename="lmu_informatik_bsc_60ects_nebenfach_stand_2023-11-22.pdf",
        note="Wird gewählt, wenn die Frage ausdrücklich das 60-ECTS-Nebenfach nennt.",
    ),
    HandbookOption(
        key="inf_bsc_minor_30",
        label="Informatik · Bachelor · Nebenfach 30 ECTS",
        program="Informatik",
        degree="Bachelor",
        variant="Nebenfach 30 ECTS",
        filename="lmu_informatik_bsc_30ects_nebenfach_stand_2023-11-22.pdf",
        note="Wird gewählt, wenn die Frage ausdrücklich das 30-ECTS-Nebenfach nennt.",
    ),
    HandbookOption(
        key="inf_msc_wise",
        label="Informatik · Master · Studienbeginn Wintersemester",
        program="Informatik",
        degree="Master",
        variant="WiSe",
        filename="lmu_informatik_msc_beginn_wise_stand_2023-01-20.pdf",
        recommended=True,
        note="Standard für Informatik-Master-Fragen, sofern kein Sommersemester genannt wird.",
    ),
    HandbookOption(
        key="inf_msc_sose",
        label="Informatik · Master · Studienbeginn Sommersemester",
        program="Informatik",
        degree="Master",
        variant="SoSe",
        filename="lmu_informatik_msc_beginn_sose_stand_2023-01-20.pdf",
        note="Wird gewählt, wenn die Frage ausdrücklich den Beginn im Sommersemester nennt.",
    ),
]


def get_handbook(key: str) -> HandbookOption:
    for handbook in HANDBOOKS:
        if handbook.key == key:
            return handbook
    raise KeyError(f"Unknown handbook key: {key}")


def recommended_keys() -> list[str]:
    return [handbook.key for handbook in HANDBOOKS if handbook.recommended]


def infer_handbook_keys(analysis: QueryAnalysis) -> list[str]:
    """Route a natural-language query to a methodically sensible corpus.

    When the query contains no program or degree information, the recommended
    four-document corpus is used. Ambiguous Informatics variants use the same
    documented defaults as the UI: integrated application subject for BSc and
    winter-semester start for MSc.
    """

    candidates = HANDBOOKS
    explicit = False

    if analysis.program:
        candidates = [h for h in candidates if h.program == analysis.program]
        explicit = True
    if analysis.degree:
        candidates = [h for h in candidates if h.degree == analysis.degree]
        explicit = True

    if analysis.variant == "Nebenfach 30 ECTS":
        candidates = [h for h in candidates if h.key == "inf_bsc_minor_30"]
        explicit = True
    elif analysis.variant == "Nebenfach 60 ECTS":
        candidates = [h for h in candidates if h.key == "inf_bsc_minor_60"]
        explicit = True
    elif analysis.variant == "Nebenfach":
        candidates = [h for h in candidates if "minor" in h.key]
        explicit = True
    elif analysis.variant == "SoSe":
        candidates = [h for h in candidates if h.key == "inf_msc_sose"]
        explicit = True
    elif analysis.variant == "WiSe":
        candidates = [h for h in candidates if h.key == "inf_msc_wise"]
        explicit = True

    if not explicit:
        return recommended_keys()

    # Resolve ambiguous Informatics variants to the documented presentation default.
    if analysis.program == "Informatik" and analysis.degree == "Bachelor" and not analysis.variant:
        return ["inf_bsc_integrated"]
    if analysis.program == "Informatik" and analysis.degree == "Master" and not analysis.variant:
        return ["inf_msc_wise"]

    keys = [h.key for h in candidates]
    return keys or recommended_keys()


def selected_filenames(selection_keys: Iterable[str]) -> set[str]:
    return {get_handbook(key).filename for key in selection_keys}


def match_chunk_to_filenames(chunk: object, filenames: set[str]) -> bool:
    """Return True if a chunk belongs to one of the selected handbook PDFs."""

    if not filenames:
        return True

    haystack_parts: list[str] = []
    if isinstance(chunk, dict):
        for key in ("source", "source_path", "doc_id", "document", "filename", "path"):
            value = chunk.get(key)
            if value:
                haystack_parts.append(str(value))
        metadata = chunk.get("metadata") or {}
        if isinstance(metadata, dict):
            haystack_parts.extend(str(v) for v in metadata.values() if v)
    else:
        for key in ("source", "source_path", "doc_id", "document", "filename", "path"):
            value = getattr(chunk, key, None)
            if value:
                haystack_parts.append(str(value))
        metadata = getattr(chunk, "metadata", None)
        if isinstance(metadata, dict):
            haystack_parts.extend(str(v) for v in metadata.values() if v)

    haystack = "\n".join(haystack_parts).lower()
    return any(
        Path(filename).name.lower() in haystack or Path(filename).stem.lower() in haystack
        for filename in filenames
    )
