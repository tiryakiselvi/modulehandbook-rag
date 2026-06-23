# Präsentations-Runbook

## Einmalige Einrichtung in CMD

```bat
cd C:\Users\ASUS\Documents\selviss\modulehandbook-rag
py -3.11 -m venv .venv
.venv\Scripts\activate
set PYTHONUTF8=1
python -m pip install --upgrade pip
python -m pip install -e .[dense,dev]
```

## Korpora identisch erzeugen

```bat
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_naive.jsonl --chunking naive
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_module.jsonl --chunking module
python -m modulehandbook_rag.cli ingest data\raw --out data\processed\chunks_field.jsonl --chunking field
python -m modulehandbook_rag.cli stats --chunks data\processed\chunks_field.jsonl
```

## Kernexperiment (für die Ergebnisfolie)

Friert für den Vergleich **BM25 vs. dense vs. hybrid** die Feld-Chunks ein und führt die drei Methoden mit `--require-section --top-k 3` aus. Für dense/hybrid wird beim ersten Lauf das Embedding-Modell geladen. Notiert Modell, Datum, Chunk-Zahl und alle Parameter. So verändert sich nur die Retrieval-Methode, nicht gleichzeitig der Granularitätsbegriff der Relevanz.

| Chunking | Retriever | Befehlskern |
|---|---|---|
| field | BM25 | `--chunks data\processed\chunks_field.jsonl --retriever bm25` |
| field | dense | `--chunks data\processed\chunks_field.jsonl --retriever dense` |
| field | hybrid | `--chunks data\processed\chunks_field.jsonl --retriever hybrid --alpha 0.5` |

Example: `python -m modulehandbook_rag.cli evaluate --chunks data\processed\chunks_field.jsonl --retriever hybrid --alpha 0.5 --top-k 3 --require-section`

Do not pool relaxed module correctness with strict field correctness in one number. The main report metric is strict Hit@1 and MRR@3; show nDCG@3 as a ranking complement. Report an optional `--section-boost 8` run separately as “BM25 + field heuristic”, never as the BM25 baseline.

## Chunking-Experiment (separat und ehrlich)

Die vorhandene Tabelle bleibt eine gute qualitative Fehleranalyse. Behaltet dort pro Frage die Top-5-Ausgabe für naive, module und field bei und bewertet: **richtiger Modulkontext**, **richtiger Abschnitt**, **Antwort direkt im Chunk**. Eine strikte Abschnittsmetrik ist nur bei Feld-Chunks definiert; für naive/module müssten eigene Gold-Chunks bzw. Evidenzspannen gelabelt werden. Das wird als nächste Ausbaustufe formuliert, nicht mit inkompatiblen Zahlen vermischt.

## Ollama demo (after retrieval evaluation)

Install Ollama from https://ollama.com/download, then in a second CMD:

```bat
ollama pull llama3.2:3b
ollama run llama3.2:3b "Antworte nur mit OK."
```

Then use the best verified corpus/retriever, for example:

```bat
python -m modulehandbook_rag.cli ask-llm "Welche Prüfungsform hat WP3 Information Retrieval?" --chunks data\processed\chunks_field.jsonl --retriever hybrid --top-k 2 --model llama3.2:3b --temperature 0
```

The LLM is a demonstration layer, not the retrieval evaluation target. Always show the retrieved source and say whether the answer is supported by it.
