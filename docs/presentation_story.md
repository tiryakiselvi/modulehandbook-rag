# Presentation story

## Slide 1: Problem

University module handbooks are semi-structured PDFs. Students ask questions such as: Which exam type does WP3 have? How many ECTS does P4 have? Which modules cover search engines?

A generic PDF chatbot can answer some of these questions, but it is hard to know whether it retrieved the exact evidence.

## Slide 2: Research question

> Does structure-aware chunking improve retrieval quality for RAG over university module handbooks?

## Slide 3: Data and structure

Module handbooks contain recurring fields: module title, ECTS, contents, prerequisites, semester, exam type, teaching language and responsible lecturer.

This structure motivates field-level chunks.

## Slide 4: Pipeline

```text
PDF → text extraction → cleanup → chunking → retrieval → grounded answer with source
```

## Slide 5: Chunking strategies

- naive: fixed windows
- module: one chunk per module
- field: one chunk per module field

Main intuition: module chunks keep context, field chunks give precise evidence.

## Slide 6: Retrieval methods

- BM25 as lexical baseline
- BM25 with section boost as domain-aware variant
- dense retrieval for semantic and multilingual queries
- hybrid retrieval for BM25+dense combination

## Slide 7: Evaluation design

Two relevance settings:

1. relaxed module-level relevance: correct module?
2. strict field-level relevance: correct module and correct answer field?

The strict setting is the most important for grounded QA.

## Slide 8: Query types

The gold set is grouped by query type:

- numerical
- exam
- responsible person
- semester
- content
- prerequisite
- language
- broad topic

This makes it possible to show where each retrieval strategy works best.

## Slide 9: Results

Use the generated tables from:

```bash
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --section-boosts 0,8
python -m modulehandbook_rag.cli benchmark --chunkings field --retrievers bm25 --top-k 3 --require-section --by-query-type --section-boosts 8
```

Suggested verbal interpretation:

> Field-level chunks are better evidence units for answer grounding. The section boost improves structured field questions, so we report it as a domain-aware retrieval variant rather than as a pure BM25 baseline.

## Slide 10: Demo

Show one German query, one English query and one Turkish query.

German:

```text
Welche Prüfungsform hat WP3 Information Retrieval?
```

English:

```text
What is the exam type for WP3 Information Retrieval?
```

Turkish:

```text
WP3 Information Retrieval dersinin sınav şekli nedir?
```

## Slide 11: Limitations

- Field parser depends on recognizable labels.
- Gold set is manually labeled and relatively small.
- Dense retrieval needs optional dependencies.
- LLM answer quality is demonstrated, not fully evaluated.
- Scanned PDFs need OCR first.

## Slide 12: Conclusion

> The project shows that RAG over module handbooks should not start with generation. It should start with evidence retrieval. Structure-aware chunking and transparent retrieval evaluation make the system more reliable and easier to inspect.
