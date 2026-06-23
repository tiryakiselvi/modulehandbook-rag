from __future__ import annotations

from .bm25_retrieval import BM25Retriever
from .dense_retrieval import DenseRetriever
from .schemas import Chunk, SearchResult


def _normalize(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], alpha: float = 0.5, section_boost: float = 0.0, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0 and 1.")
        self.chunks = chunks
        self.alpha = alpha
        self.bm25 = BM25Retriever(chunks, section_boost=section_boost)
        self.dense = DenseRetriever(chunks, model_name=model_name)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        bm25_scores = _normalize({str(i): score for i, score in enumerate(self.bm25.scores(query))})
        dense_scores = _normalize({str(i): score for i, score in enumerate(self.dense.scores(query))})
        combined = [(i, self.alpha * dense_scores[str(i)] + (1 - self.alpha) * bm25_scores[str(i)]) for i in range(len(self.chunks))]
        ranked = sorted(combined, key=lambda item: (-item[1], item[0]))[:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(score), rank=rank + 1)
            for rank, (i, score) in enumerate(ranked)
        ]
