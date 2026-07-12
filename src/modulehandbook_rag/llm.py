from __future__ import annotations
import json
import urllib.error
import urllib.request
from dataclasses import dataclass

class LLMError(RuntimeError):
    pass

@dataclass
class OllamaClient:
    model: str = "llama3.1:8b"
    base_url: str = "http://localhost:11434"
    timeout: int = 300

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False,
                              "options": {"temperature": temperature}}).encode("utf-8")
        request = urllib.request.Request(
            self.base_url.rstrip("/") + "/api/generate", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise LLMError("Ollama konnte nicht erreicht werden oder lieferte keine gültige Antwort.") from exc
        answer = str(data.get("response", "")).strip()
        if not answer:
            raise LLMError("Ollama hat keine Antwort zurückgegeben.")
        return answer
