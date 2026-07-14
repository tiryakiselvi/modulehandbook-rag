# modulehandbook-rag

Ein Retrieval-Augmented-Generation-System für Modulhandbücher. Das Projekt extrahiert Text aus Modulhandbuch-PDFs, zerlegt die Dokumente in strukturierte Chunks und sucht zu natürlichsprachlichen Fragen passende Textstellen. Die gefundenen Chunks dienen als nachvollziehbare Evidenz für eine Antwort.

## Überblick

Modulhandbücher sind lang, halb-strukturiert und enthalten viele wiederkehrende Felder, zum Beispiel ECTS, Prüfungsform, Inhalte, Voraussetzungen, Sprache oder Modulverantwortliche. Eine einfache Volltextsuche liefert dabei häufig Treffer, die zwar einzelne Wörter enthalten, aber nicht die passende Antwortstelle sind.

Dieses Projekt vergleicht deshalb unterschiedliche Chunking- und Retrieval-Strategien:

- naive Chunking
- module-level Chunking
- field-level Chunking
- BM25 Retrieval
- Dense Retrieval
- Hybrid Retrieval

Die Anwendung kann Fragen auf Deutsch, Englisch und Türkisch verarbeiten. In der kontrollierten mehrsprachigen Evaluation bleibt BM25 wegen Modulcodes, Feldnamen und Query Expansion bereits stark. Dense Retrieval allein ist schwächer; die beste Gesamtleistung erzielt Hybrid Retrieval mit einem moderaten Dense-Anteil.

## Projektstruktur

```text
modulehandbook-rag/
├── app.py
├── data/
│   ├── raw/
│   ├── eval/
│   └── processed/
├── docs/
├── outputs/
├── scripts/
├── src/
│   └── modulehandbook_rag/
├── tests/
├── pyproject.toml
└── README.md
```

## Installation

Unter Windows mit Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate

python -m pip install --upgrade pip
python -m pip install -e ".[all]"
```

Nur die Basisversion ohne Streamlit und Dense Retrieval:

```bash
python -m pip install -e .
```

## Daten

Die Modulhandbücher liegen unter `data/raw/`. Enthalten sind Modulhandbücher für Computerlinguistik und Informatik, jeweils Bachelor und Master. Bei Informatik sind zusätzlich Varianten für Nebenfach und Studienbeginn im Sommersemester beziehungsweise Wintersemester enthalten.

Die Quellen der Dokumente sind in `docs/modulhandbuch_quellen.md` dokumentiert.

## Chunks erzeugen

```bash
python -m modulehandbook_rag.cli ingest data/raw \
  --chunking field \
  --out data/processed/chunks_field.jsonl
```

Weitere Chunking-Varianten:

```bash
python -m modulehandbook_rag.cli ingest data/raw \
  --chunking module \
  --out data/processed/chunks_module.jsonl

python -m modulehandbook_rag.cli ingest data/raw \
  --chunking naive \
  --out data/processed/chunks_naive.jsonl
```

Nach einem vollständigen Release-Lauf können die bereits geprüften Vollkorpus-Chunks
direkt als lokale Demo-Daten bereitgestellt werden:

```powershell
.\scripts\prepare_demo_data.ps1 -SourceDirectory "outputs\final_release"
```

Damit verwendet die Oberfläche exakt die Chunk-Dateien des dokumentierten Abgabelaufs.

## Streamlit-App starten

```bash
python -m streamlit run app.py
```

Die App öffnet sich anschließend unter `http://localhost:8501`.

## Suche über die CLI

```bash
python -m modulehandbook_rag.cli search \
  "Welche Veranstaltung behandelt Information Retrieval?" \
  --chunks data/processed/chunks_field.jsonl \
  --retriever hybrid \
  --top-k 5
```

## Evaluation

Die Retrieval-Evaluation nutzt Gold-Queries aus `data/eval/`.

```bash
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/retrieval_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever bm25 \
  --top-k 3 \
  --require-section \
  --by-query-type
```

Für mehrsprachige Fragen:

```bash
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/multilingual_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever hybrid \
  --top-k 3 \
  --require-section \
  --by-query-type
```

Ein Beispiel für dokumentierte Ergebnisdateien liegt unter `outputs/`.

Die abschließende, methodisch getrennte Auswertung steht in [`docs/final_evaluation.md`](docs/final_evaluation.md). Reproduzierbare Rohwerte, Fragetyp-Auswertungen und die Per-Query-Fehleranalyse liegen unter `outputs/final_release/`.

Für den vollständig dokumentierten Release-Lauf unter Windows steht zusätzlich [`docs/TEST_RUNBOOK.md`](docs/TEST_RUNBOOK.md) bereit. Die dafür verwendeten direkten Paketversionen sind in `requirements-release.txt` festgehalten.

## Korpusauswahl

Wenn mehrere Modulhandbücher infrage kommen, kann das Korpus in der App explizit ausgewählt werden. Zusätzlich enthält die App eine automatische Auswahl, die Studiengang, Abschluss und Varianten wie Nebenfach oder Studienbeginn aus der Anfrage ableitet, sofern diese Informationen genannt werden.

Ohne eindeutige Angabe wird ein Standardkorpus verwendet, der Computerlinguistik Bachelor, Computerlinguistik Master, Informatik Bachelor mit integriertem Anwendungsfach und Informatik Master mit Studienbeginn im Wintersemester enthält.

## Mehrsprachige Suche

BM25 arbeitet lexikalisch und ist besonders stark, wenn die Anfrage deutsche Begriffe aus dem Modulhandbuch enthält. Dense Retrieval nutzt mehrsprachige Satzrepräsentationen. Hybrid Retrieval kombiniert beide Ansätze. In der abschließenden mehrsprachigen Evaluation erzielt `alpha = 0,25` auf 18 kontrollierten Fragen die beste Gesamtleistung. Dieser Wert ist eine datensatzbezogene Beobachtung und keine allgemeine Systemeigenschaft.

## Limitationen

Die Qualität hängt von der Struktur der Modulhandbücher, der Textqualität nach PDF-Extraktion und der Formulierung der Anfrage ab. Sehr vage Fragen sind schwieriger als Fragen mit erkennbarem Thema, Feld oder Studiengang. Generierte Antworten sollten immer zusammen mit den gefundenen Evidenzstellen betrachtet werden.
