from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from math import log2
from typing import Callable

from .schemas import Chunk, SearchResult


@dataclass
class EvalQuery:
    query: str
    relevant_modules: set[str]
    relevant_sections: set[str]
    query_id: str = ""
    query_type: str = "unspecified"

    @staticmethod
    def from_dict(data: dict) -> "EvalQuery":
        modules = data.get("relevant_modules") or data.get("module") or []
        sections = data.get("relevant_sections") or data.get("section") or []
        if isinstance(modules, str):
            modules = [x.strip() for x in modules.split(";") if x.strip()]
        if isinstance(sections, str):
            sections = [x.strip() for x in sections.split(";") if x.strip()]
        return EvalQuery(
            query=data["query"],
            relevant_modules={m.upper() for m in modules},
            relevant_sections={s for s in sections},
            query_id=str(data.get("id", data.get("query_id", ""))),
            query_type=str(data.get("query_type", "unspecified")),
        )


def load_eval_queries(path: Path) -> list[EvalQuery]:
    """Load evaluation queries from JSONL or CSV.

    JSONL example:
    {"query": "Wie viele ECTS hat WP3?", "relevant_modules": ["WP3"], "relevant_sections": ["Zugeordnete Modulteile"]}
    """
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            return [EvalQuery.from_dict(row) for row in csv.DictReader(f)]

    queries: list[EvalQuery] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                queries.append(EvalQuery.from_dict(json.loads(line)))
    return queries


def is_relevant(chunk: Chunk, query: EvalQuery, require_section: bool = False) -> bool:
    module_ok = not query.relevant_modules or (chunk.module_code or "").upper() in query.relevant_modules
    if not require_section or not query.relevant_sections:
        return module_ok
    section_ok = (chunk.section or "") in query.relevant_sections
    return module_ok and section_ok


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k == 0:
        return 0.0
    return sum(1 for item in retrieved[:k] if item in relevant) / k


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(1 for item in retrieved[:k] if item in relevant) / len(relevant)


def mrr(retrieved: list[str], relevant: set[str]) -> float:
    for idx, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / idx
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    dcg = 0.0
    for idx, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            dcg += 1 / log2(idx + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1 / log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else 0.0


def evaluate_results(
    eval_queries: list[EvalQuery],
    search_fn: Callable[[str, int], list[SearchResult]],
    corpus_chunks: list[Chunk],
    k: int = 5,
    require_section: bool = False,
) -> dict[str, float]:
    """Evaluate a retriever by checking whether retrieved chunks match gold modules/sections."""
    if not eval_queries:
        return {"queries": 0, "precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0, "ndcg@k": 0.0, "hit@1": 0.0}

    precision_scores = []
    recall_scores = []
    mrr_scores = []
    ndcg_scores = []
    hit1_scores = []

    for q in eval_queries:
        results = search_fn(q.query, k)
        if require_section:
            retrieved_ids = [r.chunk.chunk_id for r in results]
            relevant_ids = {c.chunk_id for c in corpus_chunks if is_relevant(c, q, require_section=True)}
            if not relevant_ids:
                raise ValueError(f"No gold chunk exists for strict query '{q.query}'. Check module/section labels.")
        else:
            # Relaxed retrieval means 'correct module', not 'every field of that
            # module'.  This avoids impossible recall scores for field chunks.
            retrieved_ids = list(dict.fromkeys((r.chunk.module_code or r.chunk.chunk_id).upper() for r in results))
            relevant_ids = q.relevant_modules
        # If no relevant item is retrieved, metrics below become 0.
        precision_scores.append(precision_at_k(retrieved_ids, relevant_ids, k))
        recall_scores.append(recall_at_k(retrieved_ids, relevant_ids, k))
        mrr_scores.append(mrr(retrieved_ids, relevant_ids))
        ndcg_scores.append(ndcg_at_k(retrieved_ids, relevant_ids, k))
        hit1_scores.append(1.0 if results and is_relevant(results[0].chunk, q, require_section=require_section) else 0.0)

    n = len(eval_queries)
    return {
        "queries": float(n),
        f"precision@{k}": sum(precision_scores) / n,
        f"recall@{k}": sum(recall_scores) / n,
        "mrr": sum(mrr_scores) / n,
        f"ndcg@{k}": sum(ndcg_scores) / n,
        "hit@1": sum(hit1_scores) / n,
    }


def evaluate_by_query_type(
    eval_queries: list[EvalQuery],
    search_fn: Callable[[str, int], list[SearchResult]],
    corpus_chunks: list[Chunk],
    k: int = 5,
    require_section: bool = False,
) -> dict[str, dict[str, float]]:
    """Return overall and per-question-type metrics for the report table."""
    groups: dict[str, list[EvalQuery]] = {"overall": eval_queries}
    for query in eval_queries:
        groups.setdefault(query.query_type, []).append(query)
    return {name: evaluate_results(items, search_fn, corpus_chunks, k, require_section) for name, items in groups.items()}
