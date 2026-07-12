# Evaluation results

Generate this file with:

```bash
python -m modulehandbook_rag.cli benchmark --retrievers bm25 --top-k 3 --section-boosts 8 --out-csv outputs/evaluation_results.csv --out-md docs/evaluation_results.md
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 0,8 --out-csv outputs/evaluation_results_strict.csv --out-md docs/evaluation_results_strict.md
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --by-query-type --section-boosts 8 --out-csv outputs/evaluation_by_type.csv --out-md docs/evaluation_by_type.md
python -m modulehandbook_rag.cli benchmark --eval-file data/eval/multilingual_eval_queries.jsonl --chunkings field --retrievers dense,hybrid --top-k 3 --require-section --out-csv outputs/evaluation_multilingual.csv --out-md docs/evaluation_multilingual.md
```

## Reporting template

### Module-level relevance

Paste generated table here.

### Strict field-level relevance

Paste generated table here.

### Query-type analysis

Paste generated table here.

### Multilingual retrieval

Paste generated table here.

## Interpretation template

The module-level setting answers whether the retriever finds the correct module. The strict setting answers whether it finds the exact answer-bearing field. For RAG answer grounding, the strict setting is more informative.

The section-boost ablation separates a plain BM25 baseline from the domain-aware retrieval variant. This keeps the method transparent and prevents overclaiming that all gains come from chunking alone.
