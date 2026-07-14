from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from math import log2
from pathlib import Path
from typing import Callable

from .schemas import Chunk, SearchResult


@dataclass
class EvalQuery:
    """Gold item for retrieval evaluation.

    The evaluator supports both relaxed module-level relevance and strict
    field-level relevance. Optional document labels make the same query format
    usable for multi-handbook corpora.
    """

    query: str
    relevant_modules: set[str]
    relevant_sections: set[str]
    relevant_documents: set[str] = field(default_factory=set)
    query_id: str = ""
    query_type: str = "unspecified"

    @staticmethod
    def from_dict(data: dict) -> "EvalQuery":
        modules = data.get("relevant_modules") or data.get("module") or []
        sections = data.get("relevant_sections") or data.get("section") or []
        documents = data.get("relevant_documents") or data.get("document") or []

        if isinstance(modules, str):
            modules = [x.strip() for x in modules.split(";") if x.strip()]
        if isinstance(sections, str):
            sections = [x.strip() for x in sections.split(";") if x.strip()]
        if isinstance(documents, str):
            documents = [x.strip() for x in documents.split(";") if x.strip()]

        return EvalQuery(
            query=data["query"],
            relevant_modules={m.upper() for m in modules},
            relevant_sections={s for s in sections},
            relevant_documents={Path(item).name for item in documents},
            query_id=str(data.get("id", data.get("query_id", ""))),
            query_type=str(data.get("query_type", "unspecified")),
        )


def load_eval_queries(path: Path) -> list[EvalQuery]:
    """Load evaluation queries from JSONL or CSV.

    JSONL example:
    {"id":"q01", "query":"Wie viele ECTS hat WP3?", "query_type":"numerical", "relevant_modules":["WP3"], "relevant_sections":["Zugeordnete Modulteile"]}
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


def _chunk_document_name(chunk: Chunk) -> str:
    return Path(chunk.source_path).name if chunk.source_path else ""


def is_relevant(chunk: Chunk, query: EvalQuery, require_section: bool = False) -> bool:
    """Return whether a chunk satisfies the gold labels for a query."""

    module_ok = not query.relevant_modules or (chunk.module_code or "").upper() in query.relevant_modules
    document_ok = not query.relevant_documents or _chunk_document_name(chunk) in query.relevant_documents

    if not require_section or not query.relevant_sections:
        return module_ok and document_ok

    section_ok = (chunk.section or "") in query.relevant_sections
    return module_ok and document_ok and section_ok


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


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def _module_eval_key(chunk: Chunk, query: EvalQuery) -> str:
    module = (chunk.module_code or "").upper()
    if query.relevant_documents:
        return f"{_chunk_document_name(chunk)}::{module}"
    return module


def _section_eval_key(chunk: Chunk, query: EvalQuery) -> str:
    module = (chunk.module_code or "").upper()
    section = chunk.section or ""
    if query.relevant_documents:
        return f"{_chunk_document_name(chunk)}::{module}::{section}"
    return f"{module}::{section}"


def _gold_eval_keys(query: EvalQuery, require_section: bool) -> set[str]:
    documents = query.relevant_documents or {""}
    modules = query.relevant_modules or {""}
    sections = query.relevant_sections or {""}
    if require_section:
        return {
            f"{document}::{module}::{section}" if query.relevant_documents else f"{module}::{section}"
            for document in documents
            for module in modules
            for section in sections
        }
    return {
        f"{document}::{module}" if query.relevant_documents else module
        for document in documents
        for module in modules
    }


def evaluate_results(
    eval_queries: list[EvalQuery],
    search_fn: Callable[[str, int], list[SearchResult]],
    corpus_chunks: list[Chunk],
    k: int = 5,
    require_section: bool = False,
) -> dict[str, float]:
    """Evaluate retrieval against module/document or strict field-level labels.

    Relaxed evaluation is intentionally module/document-level. This avoids
    misleading recall values for field chunks where one module may produce many
    chunks. Strict evaluation requires the exact module and field/section.
    """

    if not eval_queries:
        return {
            "queries": 0.0,
            f"precision@{k}": 0.0,
            f"recall@{k}": 0.0,
            "mrr": 0.0,
            f"ndcg@{k}": 0.0,
            "hit@1": 0.0,
        }

    precision_scores: list[float] = []
    recall_scores: list[float] = []
    mrr_scores: list[float] = []
    ndcg_scores: list[float] = []
    hit1_scores: list[float] = []

    for q in eval_queries:
        results = search_fn(q.query, k)

        if require_section:
            retrieved_ids = _dedupe_preserve_order(
                [_section_eval_key(result.chunk, q) for result in results]
            )
        else:
            retrieved_ids = _dedupe_preserve_order(
                [_module_eval_key(result.chunk, q) for result in results]
            )
        relevant_ids = _gold_eval_keys(q, require_section)

        precision_scores.append(precision_at_k(retrieved_ids, relevant_ids, k))
        recall_scores.append(recall_at_k(retrieved_ids, relevant_ids, k))
        mrr_scores.append(mrr(retrieved_ids, relevant_ids))
        ndcg_scores.append(ndcg_at_k(retrieved_ids, relevant_ids, k))
        hit1_scores.append(
            1.0
            if results and is_relevant(results[0].chunk, q, require_section=require_section)
            else 0.0
        )

    n = len(eval_queries)
    return {
        "queries": float(n),
        f"precision@{k}": sum(precision_scores) / n,
        f"recall@{k}": sum(recall_scores) / n,
        "mrr": sum(mrr_scores) / n,
        f"ndcg@{k}": sum(ndcg_scores) / n,
        "hit@1": sum(hit1_scores) / n,
    }


def evaluate_per_query(
    eval_queries: list[EvalQuery],
    search_fn: Callable[[str, int], list[SearchResult]],
    k: int = 5,
    require_section: bool = False,
) -> list[dict[str, str | int | float]]:
    """Return auditable per-query metrics using the aggregate metric units."""

    rows: list[dict[str, str | int | float]] = []
    for query in eval_queries:
        results = search_fn(query.query, k)
        if require_section:
            retrieved_ids = _dedupe_preserve_order(
                [_section_eval_key(result.chunk, query) for result in results]
            )
        else:
            retrieved_ids = _dedupe_preserve_order(
                [_module_eval_key(result.chunk, query) for result in results]
            )
        relevant_ids = _gold_eval_keys(query, require_section)
        relevant_found = sum(item in relevant_ids for item in retrieved_ids[:k])
        first_rank = next(
            (
                rank
                for rank, item in enumerate(retrieved_ids, start=1)
                if item in relevant_ids
            ),
            None,
        )
        query_precision = precision_at_k(retrieved_ids, relevant_ids, k)
        query_recall = recall_at_k(retrieved_ids, relevant_ids, k)
        query_mrr = mrr(retrieved_ids, relevant_ids)
        query_ndcg = ndcg_at_k(retrieved_ids, relevant_ids, k)
        query_hit1 = 1.0 if retrieved_ids and retrieved_ids[0] in relevant_ids else 0.0
        if query_recall == 1.0:
            result_label = "vollständig"
        elif relevant_found:
            result_label = "teilweise"
        else:
            result_label = "nicht gefunden"
        top = results[0].chunk if results else None
        rows.append(
            {
                "query_id": query.query_id,
                "query_type": query.query_type,
                "query": query.query,
                "matching": "module+section" if require_section else "module",
                "expected_document": ";".join(sorted(query.relevant_documents)),
                "expected_module": ";".join(sorted(query.relevant_modules)),
                "expected_section": ";".join(sorted(query.relevant_sections)),
                "top1_document": _chunk_document_name(top) if top else "",
                "top1_module": (top.module_code or "") if top else "",
                "top1_section": (top.section or "") if top else "",
                "first_relevant_rank": first_rank if first_rank is not None else "",
                "relevant_keys": " | ".join(sorted(relevant_ids)),
                f"retrieved_keys@{k}": " | ".join(retrieved_ids[:k]),
                "relevant_total": len(relevant_ids),
                f"relevant_found@{k}": relevant_found,
                f"precision@{k}": query_precision,
                f"recall@{k}": query_recall,
                "reciprocal_rank": query_mrr,
                f"ndcg@{k}": query_ndcg,
                "hit@1": query_hit1,
                "result": result_label,
            }
        )
    return rows


def evaluate_by_query_type(
    eval_queries: list[EvalQuery],
    search_fn: Callable[[str, int], list[SearchResult]],
    corpus_chunks: list[Chunk],
    k: int = 5,
    require_section: bool = False,
) -> dict[str, dict[str, float]]:
    """Return overall and per-query-type metrics for reporting."""

    groups: dict[str, list[EvalQuery]] = {"overall": eval_queries}
    for query in eval_queries:
        groups.setdefault(query.query_type, []).append(query)

    return {
        name: evaluate_results(items, search_fn, corpus_chunks, k, require_section)
        for name, items in groups.items()
    }
