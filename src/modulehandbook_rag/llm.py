from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class LLMError(RuntimeError):
    """Raised when an LLM backend cannot return an answer."""


@dataclass
class OllamaClient:
    """Minimal client for local Ollama text generation.

    This keeps the project lightweight: no SDK dependency is required. Ollama must
    be running locally, usually at http://localhost:11434.
    """

    model: str = "llama3.1:8b"
    base_url: str = "http://localhost:11434"
    timeout: int = 300

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        url = self.base_url.rstrip("/") + "/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise LLMError(
                "Ollama konnte nicht erreicht werden. Starte Ollama und lade ein Modell, "
                "z. B. `ollama pull llama3.1:8b`."
            ) from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Unerwartete Ollama-Antwort: {body[:300]}") from exc

        answer = parsed.get("response", "").strip()
        if not answer:
            raise LLMError(f"Ollama hat keine Antwort zurückgegeben: {body[:300]}")
        return answer
