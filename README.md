# Structure-aware Retrieval for LMU Module Handbooks

**Seminar:** Suchmaschinen und Retrieval-Augmented Generation, LMU Munich
**Authors:** Selvinaz Tiryaki and Salem Debebe

## Project motivation

University module handbooks are semi-structured documents: they combine short factual fields such as ECTS credits, examination format and teaching language with longer content descriptions. A generic PDF chat interface does not make this structure explicit. This project investigates how chunking granularity and retrieval method affect the quality of evidence retrieval for study-program questions.

The current pilot corpus is the Bachelor Computerlinguistics module handbook. The intended extension covers Bachelor and Master module handbooks, study plans, examination regulations and amendment statutes.

## Research questions

1. How do naive fixed-size, module-level and field-level chunks behave for factual and content-oriented questions?
2. How do lexical BM25, dense retrieval and hybrid retrieval differ for exact fields and broad semantic topics?
3. Does explicit document structure improve retrieval of answer-bearing evidence?

## Pipeline

```text
PDF / TXT / Markdown
        -> text cleaning
        -> chunking (naive | module | field)
        -> retrieval (BM25 | dense | hybrid)
        -> cited evidence
        -> optional local LLM answer via Ollama
```

The retrieval result is evaluated before answer generation. The optional LLM receives only retrieved context and the answer always retains its sources.

## Repository structure

```text
src/modulehandbook_rag/  Application code and CLI
data/eval/               Manually labelled evaluation queries
data/raw/                Local source documents (not versioned)
data/processed/          Local generated chunk files (not versioned)
RESULTS_2026-06-23.md    Pilot result table and interpretation
RUNBOOK_DE.md            Windows experiment and demo guide
```

See [DATASET.md](DATASET.md) for the handling of source documents.

## Installation

The commands below use Python 3.11 on Windows.

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
set PYTHONUTF8=1
python -m pip install --upgrade pip
python -m pip install -e .[dense,dev]
```

## Reproducing the pilot

Place an official module handbook PDF in `data/raw/`, then create the three chunk corpora:

```bat
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_naive.jsonl --chunking naive
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_module.jsonl --chunking module
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_field.jsonl --chunking field
```

Evaluate the three retrieval methods on the fixed field-level corpus. `--require-section` requires both the correct module and the answer-bearing field.

```bat
python -m modulehandbook_rag.cli evaluate --chunks data\processed\chunks_field.jsonl --retriever bm25 --top-k 3 --require-section
python -m modulehandbook_rag.cli evaluate --chunks data\processed\chunks_field.jsonl --retriever dense --top-k 3 --require-section
python -m modulehandbook_rag.cli evaluate --chunks data\processed\chunks_field.jsonl --retriever hybrid --alpha 0.5 --top-k 3 --require-section
```

`--section-boost 0` is the lexical BM25 baseline. A non-zero value is an explicitly reported document-structure heuristic, not part of the baseline.

## Pilot findings

On the current eight-query pilot set, BM25 is strong for exact module codes and structured fields. Dense retrieval improves broad topic search, while hybrid retrieval increases overall ranking quality and recall with `alpha = 0.5`. Details, parameters and limitations are documented in [RESULTS_2026-06-23.md](RESULTS_2026-06-23.md).

These are exploratory results. The current gold set is small and manually labelled; it should be expanded and separated into development and test data before tuning any retrieval parameter.

## Optional Ollama demo

After installing Ollama and downloading a local model, a grounded answer can be generated from retrieved evidence:

```bat
ollama pull llama3.2:3b
python -m modulehandbook_rag.cli ask-llm "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data\processed\chunks_field.jsonl --retriever hybrid --top-k 2 --model llama3.2:3b --temperature 0
```

## Limitations and next steps

- Extend the corpus with Master documents and additional academic document types.
- Increase the labelled query set and separate parameter development from final evaluation.
- Label evidence spans for a strictly comparable cross-chunking evaluation.
- Evaluate multilingual queries as a separate condition while keeping gold evidence fixed.
