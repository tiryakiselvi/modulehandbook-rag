# modulehandbook-rag

A retrieval-augmented search system for university module handbooks.

The project focuses on finding answer-bearing evidence in semi-structured module handbook documents. It supports multiple chunking strategies and retrieval methods, and provides both a command-line interface and a Streamlit interface for interactive search.

## Features

- Ingestion of PDF, TXT, and Markdown documents
- Text cleaning and normalization
- Three chunking strategies:
  - naive text chunks
  - module-level chunks
  - field-level chunks
- Retrieval methods:
  - BM25
  - dense retrieval with sentence-transformers
  - hybrid retrieval
- Evidence-first answers with source references
- Multilingual query support for German, English, and Turkish
- Evaluation with common retrieval metrics
- Streamlit interface for interactive exploration

## Project structure

```text
modulehandbook-rag/
├── app.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── eval/
├── docs/
├── src/modulehandbook_rag/
├── tests/
├── pyproject.toml
└── README.md
```

## Installation

The project is developed for Python 3.12.

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[all]"
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Data

Place module handbook PDFs in:

```text
data/raw/
```

The system can process multiple handbooks and keep document metadata during retrieval, so results can be traced back to their source document.

## Create chunks

Field-level chunking is the recommended default for precise evidence retrieval.

```bash
python -m modulehandbook_rag.cli ingest data/raw \
  --chunking field \
  --out data/processed/chunks_field.jsonl
```

Other chunking modes are available as well:

```bash
python -m modulehandbook_rag.cli ingest data/raw \
  --chunking module \
  --out data/processed/chunks_module.jsonl

python -m modulehandbook_rag.cli ingest data/raw \
  --chunking naive \
  --out data/processed/chunks_naive.jsonl
```

## Command-line search

```bash
python -m modulehandbook_rag.cli search \
  --chunks data/processed/chunks_field.jsonl \
  --query "Welche Prüfungsform hat Information Retrieval?" \
  --retriever bm25 \
  --top-k 5
```

Dense retrieval:

```bash
python -m modulehandbook_rag.cli search \
  --chunks data/processed/chunks_field.jsonl \
  --query "Which course covers information retrieval?" \
  --retriever dense \
  --top-k 5
```

Hybrid retrieval:

```bash
python -m modulehandbook_rag.cli search \
  --chunks data/processed/chunks_field.jsonl \
  --query "Bilgi erişimi ile ilgili hangi ders var?" \
  --retriever hybrid \
  --top-k 5
```

## Streamlit interface

After chunk generation, start the interface with:

```bash
python -m streamlit run app.py
```

The interface supports corpus selection, retrieval configuration, multilingual queries, and evidence inspection.

## Retrieval approach

The system is designed around evidence retrieval rather than unrestricted text generation. A query is matched against structured chunks, and the retrieved evidence is shown with metadata such as module, section, score, and source document.

BM25 works well for German queries that share terminology with the handbook text. Dense and hybrid retrieval are useful for semantic queries and multilingual queries, especially when the wording differs from the original German document text.

## Evaluation

Evaluation files are stored in:

```text
data/eval/
```

Run retrieval evaluation with:

```bash
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/retrieval_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever bm25 \
  --top-k 5 \
  --require-section
```

The evaluation reports retrieval-oriented metrics such as Hit@1, MRR, nDCG@k, Precision@k, and Recall@k.

## Multilingual queries

The handbooks are primarily written in German. German queries can be handled well by BM25 or hybrid retrieval. English and Turkish queries should use dense or hybrid retrieval because these methods can match semantically related formulations across languages.

## Limitations

- Retrieval quality depends on the structure and consistency of the input documents.
- Very vague queries may not contain enough information to identify the intended module or section.
- Dense retrieval requires additional dependencies and downloads a sentence-transformers model on first use.
- Generated answers, when enabled, should be interpreted together with the retrieved evidence.

## License

Add the appropriate license for the project before publication if needed.
