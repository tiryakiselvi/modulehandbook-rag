from __future__ import annotations

import hashlib
import os
import re

import numpy as np

from .bm25_retrieval import chunk_index_text
from .schemas import Chunk, SearchResult


class DenseRetriever:
    """Dense-style retrieval with an automatic local fallback."""

    def __init__(self, chunks: list[Chunk], model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.chunks = chunks
        texts = [chunk_index_text(c) for c in chunks]

        use_external_model = os.environ.get("MODULEHANDBOOK_USE_SENTENCE_TRANSFORMERS") == "1"
        if not use_external_model:
            self.model = None
            self.dim = 4096
            self.embeddings = np.vstack([self._local_encode(text) for text in texts])
            return

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.embeddings = self.model.encode(texts, normalize_embeddings=True)
        except Exception:
            self.model = None
            self.dim = 4096
            self.embeddings = np.vstack([self._local_encode(text) for text in texts])

    def _local_features(self, text: str):
        text = text.lower()
        for token in re.findall(r"\w+", text, flags=re.UNICODE):
            yield "w:" + token
        compact = re.sub(r"\s+", " ", text)
        for n in (3, 4, 5):
            if len(compact) >= n:
                for i in range(len(compact) - n + 1):
                    yield f"c{n}:" + compact[i : i + n]

    def _local_encode(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        for feature in self._local_features(text):
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=4).digest()
            vec[int.from_bytes(digest, "little") % self.dim] += 1.0
        norm = float(np.linalg.norm(vec))
        if norm:
            vec /= norm
        return vec

    def scores(self, query: str) -> list[float]:
        if self.model is None:
            q = self._local_encode(query)
        else:
            q = self.model.encode([query], normalize_embeddings=True)[0]
        return [float(score) for score in np.dot(self.embeddings, q)]

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        scores = self.scores(query)
        ranked = sorted(enumerate(scores), key=lambda item: (-item[1], item[0]))[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
