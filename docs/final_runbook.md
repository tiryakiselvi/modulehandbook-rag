# Final runbook

This runbook is written for a clean presentation run. All commands are relative to the repository root.

## 1. Environment

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .[all]
```

## 2. Build chunks

```bash
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_naive.jsonl --chunking naive
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_module.jsonl --chunking module
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_field.jsonl --chunking field --config configs/lmu_cl_bachelor.json
python -m modulehandbook_rag.cli stats --chunks data/processed/chunks_field.jsonl
```

Expected narrative: naive chunks are a baseline, module chunks preserve module context, field chunks are the most precise evidence units.

## 3. Demo queries

```bash
python -m modulehandbook_rag.cli search "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --retriever bm25 --top-k 3 --section-boost 8
python -m modulehandbook_rag.cli ask "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --retriever bm25 --top-k 1 --section-boost 8
python -m modulehandbook_rag.cli search "What is the exam type for WP3 Information Retrieval?" --chunks data/processed/chunks_field.jsonl --retriever dense --top-k 3
python -m modulehandbook_rag.cli search "WP3 Information Retrieval dersinin sınav şekli nedir?" --chunks data/processed/chunks_field.jsonl --retriever dense --top-k 3
```

## 4. Evaluation commands

Relaxed module-level comparison:

```bash
python -m modulehandbook_rag.cli benchmark --retrievers bm25 --top-k 3 --section-boosts 8 --out-csv outputs/evaluation_results.csv --out-md docs/evaluation_results.md
```

Strict field-level comparison with BM25 ablation:

```bash
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 0,8 --out-csv outputs/evaluation_results_strict.csv --out-md docs/evaluation_results_strict.md
```

Per-query-type analysis:

```bash
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 8 --by-query-type --out-csv outputs/evaluation_by_type.csv --out-md docs/evaluation_by_type.md
```

Dense/hybrid multilingual evaluation:

```bash
python -m modulehandbook_rag.cli benchmark --eval-file data/eval/multilingual_eval_queries.jsonl --chunkings field --retrievers dense,hybrid --top-k 3 --require-section --out-csv outputs/evaluation_multilingual.csv --out-md docs/evaluation_multilingual.md
```

## 5. Streamlit demo

```bash
streamlit run app.py
```

Recommended demo order:

1. Show built-in field chunks.
2. Ask the WP3 exam-form question.
3. Open the ranked evidence and point to module, section and source.
4. Switch to dense retrieval for an English or Turkish query.
5. Emphasize that the LLM answer is grounded in retrieved evidence, not evaluated as a standalone chatbot.

## 6. Final presentation claim

Use this exact wording:

> The core contribution is not the LLM interface. The core contribution is a structure-aware retrieval pipeline and an evaluation setup that checks whether the system retrieves the correct answer-bearing evidence from semi-structured module handbooks.
