from __future__ import annotations

import numpy as np

from .bm25_retrieval import chunk_index_text
from .schemas import Chunk, SearchResult


class DenseRetriever:
    """Dense retrieval with sentence-transformers.

    This dependency is optional. Install with: pip install -e .[dense]
    """

    def __init__(self, chunks: list[Chunk], model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError("Install dense dependencies with: pip install -e .[dense]") from exc

        self.chunks = chunks
        self.model = SentenceTransformer(model_name)
        self.embeddings = self.model.encode([chunk_index_text(c) for c in chunks], normalize_embeddings=True)

    def scores(self, query: str) -> list[float]:
        q = self.model.encode([query], normalize_embeddings=True)[0]
        return [float(score) for score in np.dot(self.embeddings, q)]

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        scores = self.scores(query)
        ranked = sorted(enumerate(scores), key=lambda item: (-item[1], item[0]))[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
