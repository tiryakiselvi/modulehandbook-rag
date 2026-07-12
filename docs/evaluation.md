# Evaluation methodology

The evaluation focuses on retrieval quality. LLM answers are demonstrated, but the reported metrics are computed before generation.

## Gold labels

Each query has:

- `id`: stable query identifier
- `query`: natural-language question
- `query_type`: category such as `numerical`, `exam`, `content`, `semester`, `responsible_person`, `language`, `prerequisite` or `broad_topic`
- `relevant_documents`: optional handbook filenames for multi-document corpora
- `relevant_modules`: relevant module codes such as `WP3`
- `relevant_sections`: relevant module fields such as `Form der Modulprüfung`

## Two relevance settings

### Relaxed module-level relevance

A result is relevant if it belongs to the correct module. This setting is useful for comparing chunking strategies at module-identification level.

### Strict field-level relevance

A result is relevant only if it belongs to the correct module and the correct field/section. This is the main setting for RAG answer grounding because the generated answer should be based on the exact answer-bearing evidence.

## Metrics

- `hit@1`: whether the first ranked result is relevant
- `precision@k`: share of the top-k retrieved items that are relevant
- `recall@k`: share of all relevant items retrieved in the top-k
- `mrr`: mean reciprocal rank
- `ndcg@k`: ranking quality with higher weight for relevant items near the top

## Ablation

BM25 is reported in two variants:

- `section_boost = 0`: ablation baseline
- `section_boost = 8`: domain-aware field boost

This distinction is important. If field-level results improve, the presentation should not attribute the improvement to chunking alone. The final method combines structure-aware chunks with domain-aware retrieval.

## Recommended commands

```bash
python -m modulehandbook_rag.cli benchmark --retrievers bm25 --top-k 3
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 0,8
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --by-query-type --section-boosts 8
python -m modulehandbook_rag.cli benchmark --eval-file data/eval/multilingual_eval_queries.jsonl --chunkings field --retrievers dense,hybrid --top-k 3 --require-section
```
