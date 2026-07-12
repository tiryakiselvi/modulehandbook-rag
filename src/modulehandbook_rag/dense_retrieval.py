from __future__ import annotations
import numpy as np
from .bm25_retrieval import chunk_index_text
from .schemas import Chunk, SearchResult

class DenseRetriever:
    def __init__(self, chunks: list[Chunk], model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        if not chunks:
            raise ValueError("Cannot build retriever with zero chunks.")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("Dense Retrieval benötigt sentence-transformers.") from exc
        self.chunks = chunks
        self.model = SentenceTransformer(model_name)
        self.embeddings = self.model.encode(
            [chunk_index_text(chunk) for chunk in chunks],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        vector = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
        scores = np.dot(self.embeddings, vector)
        ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)[:top_k]
        return [SearchResult(self.chunks[index], float(score), rank + 1)
                for rank, (index, score) in enumerate(ranked)]
