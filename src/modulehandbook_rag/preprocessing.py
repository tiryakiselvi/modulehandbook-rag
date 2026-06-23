from __future__ import annotations

import re
import unicodedata

_UMLAUT_FIXES = {
    "a": "ä", "o": "ö", "u": "ü",
    "A": "Ä", "O": "Ö", "U": "Ü",
}


def _repair_pdf_umlauts(text: str) -> str:
    """Repair common PDF extraction artifacts for German umlauts.

    Some PDFs extract `ü` as ` ̈u` or `u ̈`. This breaks section labels like
    `Form der Modulprüfung`. The rules below fix the common cases while keeping
    the original text otherwise unchanged.
    """
    # Case 1: the combining diaeresis or spacing diaeresis appears before vowel:
    # `Pr ̈ufung`, `f ¨ur`, `Einf ̈uhrung`.
    for plain, umlaut in _UMLAUT_FIXES.items():
        text = re.sub(rf"\s*[\u0308\u00a8]\s*{plain}", umlaut, text)

    # Case 2: vowel followed by diaeresis: `u ̈`, `a ¨`.
    for plain, umlaut in _UMLAUT_FIXES.items():
        text = re.sub(rf"{plain}\s*[\u0308\u00a8]", umlaut, text)
    return text


def clean_text(text: str) -> str:
    """Normalize PDF-extracted text while preserving German characters."""
    text = text.replace("\u00ad", "")
    text = text.replace("￾", " ")
    text = _repair_pdf_umlauts(text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)  # de-hyphenate line breaks
    text = re.sub(r"(?<!\n)\n(?!\n)", "\n", text)
    return text.strip()


def tokenize_german(text: str) -> list[str]:
    """Simple tokenizer suitable for BM25 baseline."""
    text = clean_text(text).lower()
    return re.findall(r"[a-zäöüß0-9]+", text, flags=re.IGNORECASE)
