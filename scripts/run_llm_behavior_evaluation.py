from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from modulehandbook_rag.bm25_retrieval import BM25Retriever
from modulehandbook_rag.llm import OllamaClient
from modulehandbook_rag.rag import llm_answer_from_results
from modulehandbook_rag.utils import read_jsonl


ROOT = Path(__file__).resolve().parents[1]
ABSTENTION = "Diese Information ist im bereitgestellten Kontext nicht enthalten."
CLARIFICATION = "Bitte präzisieren Sie"


def _classify(answer: str) -> str:
    if answer.strip().startswith(CLARIFICATION):
        return "clarify"
    if ABSTENTION in answer:
        return "abstain"
    return "answer"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--model", default="llama3.2:3b")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    official_chunks = read_jsonl(args.results / "chunks" / "official_cl_bsc_field.jsonl")
    curated_chunks = read_jsonl(args.results / "chunks" / "curated_main_field.jsonl")
    official = BM25Retriever(official_chunks, section_boost=8.0, use_query_expansion=True)
    curated = BM25Retriever(curated_chunks, section_boost=8.0, use_query_expansion=True)
    client = OllamaClient(model=args.model)
    queries = [
        json.loads(line)
        for line in (ROOT / "data" / "eval" / "answerability_eval_queries.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]

    rows: list[dict] = []
    answers_by_query: dict[str, list[str]] = defaultdict(list)
    for item in queries:
        retriever = curated if item["category"] == "ambiguous" else official
        results = retriever.search(item["query"], top_k=3)
        for repeat in range(1, args.repeats + 1):
            answer = llm_answer_from_results(
                item["query"],
                results,
                lambda prompt: client.generate(
                    prompt, temperature=0.0, seed=args.seed
                ),
            )
            observed = _classify(answer)
            answers_by_query[item["id"]].append(answer)
            rows.append(
                {
                    "query_id": item["id"],
                    "category": item["category"],
                    "query": item["query"],
                    "expected_behavior": item["expected_behavior"],
                    "repeat": repeat,
                    "observed_behavior": observed,
                    "behavior_correct": observed == item["expected_behavior"],
                    "answer": answer,
                    "retrieved_sources": "; ".join(
                        f"{Path(result.chunk.source_path).name}:{result.chunk.module_code}:{result.chunk.section}"
                        for result in results
                    ),
                }
            )

    for row in rows:
        row["exactly_reproducible"] = len(set(answers_by_query[row["query_id"]])) == 1

    out = args.results / "llm_behavior"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "llm_behavior_runs.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "model": args.model,
        "temperature": 0.0,
        "seed": args.seed,
        "repeats": args.repeats,
        "queries": len(queries),
        "behavior_accuracy": sum(row["behavior_correct"] for row in rows) / len(rows),
        "exact_reproducibility": sum(
            len(set(answers)) == 1 for answers in answers_by_query.values()
        ) / len(answers_by_query),
    }
    (out / "llm_behavior_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
