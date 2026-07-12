#!/usr/bin/env bash
set -euo pipefail
mkdir -p outputs
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/retrieval_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever bm25 \
  --top-k 3 \
  --require-section \
  --by-query-type \
  > outputs/evaluation_bm25_field.txt
