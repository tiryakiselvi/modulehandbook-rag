from __future__ import annotations
import re
import unicodedata

_UMLAUT_FIXES = {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü"}

def _repair_pdf_umlauts(text: str) -> str:
    for plain, umlaut in _UMLAUT_FIXES.items():
        text = re.sub(rf"\s*[\u0308\u00a8]\s*{plain}", umlaut, text)
        text = re.sub(rf"{plain}\s*[\u0308\u00a8]", umlaut, text)
    return text

def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("￾", " ")
    text = _repair_pdf_umlauts(text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def tokenize_german(text: str) -> list[str]:
    return re.findall(r"[a-zäöüß0-9]+", clean_text(text).lower(), flags=re.IGNORECASE)
