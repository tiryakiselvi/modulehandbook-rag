#!/usr/bin/env bash
set -euo pipefail
mkdir -p outputs
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/multilingual_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever hybrid \
  --top-k 3 \
  --require-section \
  --by-query-type \
  > outputs/evaluation_hybrid_multilingual.txt
