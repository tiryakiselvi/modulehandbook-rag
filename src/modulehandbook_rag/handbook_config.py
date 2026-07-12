from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODULE_PATTERN = r"(?im)^\s*Modul:\s+([A-Z]{1,4}\s*\d+[A-Z]?|[A-Z]{2,})\s+([^\n]+)"
DEFAULT_SECTION_LABELS = (
    "Englischer Modultitel", "Zuordnung zum Studiengang", "Zugeordnete Modulteile",
    "Art des Moduls", "Verwendbarkeit des Moduls", "Wahlpflichtregelungen",
    "Teilnahmevoraussetzung", "Zeitpunkt im Studienverlauf", "Dauer", "Inhalte",
    "Qualifikationsziele", "Form der Modulprüfung", "Form der Modulprufung",
    "Art der Bewertung", "Voraussetzung für die Vergabe", "Voraussetzung fur die Vergabe",
    "Modulverantwortliche/r", "Unterrichtssprache", "Sonstige Informationen",
)

@dataclass(frozen=True)
class HandbookConfig:
    name: str = "default"
    module_pattern: str = DEFAULT_MODULE_PATTERN
    section_labels: tuple[str, ...] = DEFAULT_SECTION_LABELS

def load_handbook_config(path: Path | None) -> HandbookConfig:
    if path is None:
        return HandbookConfig()
    data = json.loads(path.read_text(encoding="utf-8"))
    return HandbookConfig(
        name=str(data.get("name", path.stem)),
        module_pattern=str(data.get("module_pattern", DEFAULT_MODULE_PATTERN)),
        section_labels=tuple(data.get("section_labels", DEFAULT_SECTION_LABELS)),
    )
