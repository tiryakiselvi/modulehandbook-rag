from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
from pathlib import Path

from modulehandbook_rag.bm25_retrieval import BM25Retriever
from modulehandbook_rag.chunking import make_chunks
from modulehandbook_rag.data_loader import load_documents
from modulehandbook_rag.evaluation import (
    evaluate_by_query_type,
    evaluate_per_query,
    evaluate_results,
    load_eval_queries,
)
from modulehandbook_rag.hybrid_retrieval import HybridRetriever
from modulehandbook_rag.utils import write_jsonl


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CL_BSC = "lmu_computerlinguistik_bsc_stand_2025-09-24.pdf"
CURATED_MAIN = (
    CL_BSC,
    "lmu_computerlinguistik_msc_stand_2025-07-08.pdf",
    "lmu_informatik_bsc_integriertes_anwendungsfach_stand_2023-11-22.pdf",
    "lmu_informatik_msc_beginn_wise_stand_2023-01-20.pdf",
)


def _documents(names: tuple[str, ...]) -> list:
    docs = []
    for name in names:
        docs.extend(load_documents(RAW / name))
    return docs


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _metric_row(
    series: str,
    query_set: str,
    corpus: str,
    chunking: str,
    retriever: str,
    matching: str,
    metrics: dict[str, float],
    section_boost: float | str = "",
    query_expansion: bool | str = "",
    alpha: float | str = "",
) -> dict:
    return {
        "series": series,
        "query_set": query_set,
        "n": int(metrics["queries"]),
        "corpus": corpus,
        "chunking": chunking,
        "retriever": retriever,
        "top_k": 3,
        "matching": matching,
        "section_boost": section_boost,
        "query_expansion": query_expansion,
        "alpha": alpha,
        "precision@3": metrics["precision@3"],
        "recall@3": metrics["recall@3"],
        "mrr": metrics["mrr"],
        "ndcg@3": metrics["ndcg@3"],
        "hit@1": metrics["hit@1"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "final_evaluation")
    args = parser.parse_args()
    out = args.out.resolve()
    chunk_dir = out / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    corpora = {
        "official_cl_bsc": (CL_BSC,),
        "curated_main": CURATED_MAIN,
        "stress_all_variants": tuple(path.name for path in sorted(RAW.glob("*.pdf"))),
    }
    chunks: dict[tuple[str, str], list] = {}
    integrity_rows: list[dict] = []

    for corpus_name, filenames in corpora.items():
        docs = _documents(filenames)
        for mode in ("naive", "module", "field"):
            current = make_chunks(docs, mode=mode)
            chunks[(corpus_name, mode)] = current
            write_jsonl(current, chunk_dir / f"{corpus_name}_{mode}.jsonl")
            ids = [chunk.chunk_id for chunk in current]
            integrity_rows.append(
                {
                    "corpus": corpus_name,
                    "documents": len(filenames),
                    "chunking": mode,
                    "chunks": len(current),
                    "unique_chunk_ids": len(set(ids)),
                    "duplicate_chunk_ids": len(ids) - len(set(ids)),
                    "chunks_without_module": sum(not chunk.module_code for chunk in current),
                }
            )

    german = load_eval_queries(ROOT / "data" / "eval" / "retrieval_eval_queries.jsonl")
    multilingual = load_eval_queries(ROOT / "data" / "eval" / "multilingual_eval_queries.jsonl")
    metric_rows: list[dict] = []
    detail_rows: list[dict] = []
    type_rows: list[dict] = []

    for mode in ("naive", "module", "field"):
        current = chunks[("official_cl_bsc", mode)]
        retriever = BM25Retriever(current, section_boost=8.0, use_query_expansion=True)
        metrics = evaluate_results(german, retriever.search, current, k=3, require_section=False)
        metric_rows.append(
            _metric_row(
                "chunking_comparison",
                "Deutsch n=25",
                "official_cl_bsc",
                mode,
                "BM25",
                "module",
                metrics,
                8.0,
                True,
            )
        )

    field = chunks[("official_cl_bsc", "field")]
    bm25_variants = (
        ("BM25_plain", BM25Retriever(field, section_boost=0.0, use_query_expansion=False), 0.0, False),
        ("BM25_expansion", BM25Retriever(field, section_boost=0.0, use_query_expansion=True), 0.0, True),
        ("BM25_domain", BM25Retriever(field, section_boost=8.0, use_query_expansion=True), 8.0, True),
    )
    for name, retriever, boost, expansion in bm25_variants:
        metrics = evaluate_results(german, retriever.search, field, k=3, require_section=True)
        metric_rows.append(
            _metric_row(
                "bm25_ablation", "Deutsch n=25", "official_cl_bsc", "field",
                name, "module+section", metrics, boost, expansion,
            )
        )

    hybrid = HybridRetriever(field, alpha=0.5, section_boost=8.0, use_query_expansion=True)
    dense = hybrid.dense
    for query_name, queries in (("Deutsch n=25", german), ("Mehrsprachig n=18", multilingual)):
        dense_metrics = evaluate_results(queries, dense.search, field, k=3, require_section=True)
        metric_rows.append(
            _metric_row(
                "retriever_comparison", query_name, "official_cl_bsc", "field",
                "Dense", "module+section", dense_metrics,
            )
        )
        bm25 = BM25Retriever(field, section_boost=8.0, use_query_expansion=True)
        bm25_metrics = evaluate_results(queries, bm25.search, field, k=3, require_section=True)
        metric_rows.append(
            _metric_row(
                "retriever_comparison", query_name, "official_cl_bsc", "field",
                "BM25_domain", "module+section", bm25_metrics, 8.0, True,
            )
        )
        for alpha in (0.25, 0.5, 0.75):
            hybrid.alpha = alpha
            hybrid_metrics = evaluate_results(
                queries, hybrid.search, field, k=3, require_section=True
            )
            metric_rows.append(
                _metric_row(
                    "alpha_sweep", query_name, "official_cl_bsc", "field",
                    "Hybrid", "module+section", hybrid_metrics, 8.0, True, alpha,
                )
            )

    best_bm25 = BM25Retriever(field, section_boost=8.0, use_query_expansion=True)
    hybrid.alpha = 0.5
    for system_name, retriever, queries, query_set in (
        ("BM25_domain", best_bm25, german, "Deutsch n=25"),
        ("Dense", dense, german, "Deutsch n=25"),
        ("Hybrid_alpha_0.50", hybrid, german, "Deutsch n=25"),
        ("BM25_domain", best_bm25, multilingual, "Mehrsprachig n=18"),
        ("Dense", dense, multilingual, "Mehrsprachig n=18"),
        ("Hybrid_alpha_0.50", hybrid, multilingual, "Mehrsprachig n=18"),
    ):
        for row in evaluate_per_query(queries, retriever.search, k=3, require_section=True):
            detail_rows.append({"query_set": query_set, "system": system_name, **row})
        grouped = evaluate_by_query_type(
            queries, retriever.search, field, k=3, require_section=True
        )
        for query_type, metrics in grouped.items():
            type_rows.append(
                {
                    "query_set": query_set,
                    "system": system_name,
                    "query_type": query_type,
                    **metrics,
                }
            )

    for corpus_name in ("curated_main", "stress_all_variants"):
        current = chunks[(corpus_name, "field")]
        retriever = BM25Retriever(current, section_boost=8.0, use_query_expansion=True)
        metrics = evaluate_results(german, retriever.search, current, k=3, require_section=True)
        metric_rows.append(
            _metric_row(
                "corpus_robustness", "Deutsch n=25", corpus_name, "field",
                "BM25_domain", "module+section", metrics, 8.0, True,
            )
        )

    _write_csv(out / "retrieval_metrics.csv", metric_rows)
    _write_csv(out / "query_type_metrics.csv", type_rows)
    _write_csv(out / "per_query_analysis.csv", detail_rows)
    _write_csv(out / "chunk_integrity.csv", integrity_rows)

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()
    metadata = {
        "commit": commit,
        "python": platform.python_version(),
        "german_queries": len(german),
        "multilingual_queries": len(multilingual),
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "official_corpus": list(corpora["official_cl_bsc"]),
        "curated_main_corpus": list(corpora["curated_main"]),
        "stress_corpus": list(corpora["stress_all_variants"]),
        "evaluation_note": (
            "Official quality metrics use the CL-BSc Gold set. Curated and all-variant "
            "rows are robustness diagnostics with the same CL-BSc questions."
        ),
    }
    (out / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(out)


if __name__ == "__main__":
    main()
