#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/processed
python -m modulehandbook_rag.cli ingest data/raw \
  --chunking field \
  --out data/processed/chunks_field.jsonl
