@echo off
setlocal

python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_naive.jsonl --chunking naive
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_module.jsonl --chunking module
python -m modulehandbook_rag.cli ingest data/raw --out data/processed/chunks_field.jsonl --chunking field --config configs/lmu_cl_bachelor.json

python -m modulehandbook_rag.cli benchmark --retrievers bm25 --top-k 3 --section-boosts 8 --out-csv outputs/evaluation_results.csv --out-md docs/evaluation_results.md
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 0,8 --out-csv outputs/evaluation_results_strict.csv --out-md docs/evaluation_results_strict.md
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --by-query-type --section-boosts 8 --out-csv outputs/evaluation_by_type.csv --out-md docs/evaluation_by_type.md
python -m modulehandbook_rag.cli benchmark --eval-file data/eval/multilingual_eval_queries.jsonl --chunkings field --retrievers dense,hybrid --top-k 3 --require-section --out-csv outputs/evaluation_multilingual.csv --out-md docs/evaluation_multilingual.md

endlocal
