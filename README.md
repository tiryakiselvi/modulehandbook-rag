# Modulhandbuch-RAG

Struktur-aware Retrieval für LMU-Modulhandbücher im Seminar **Suchmaschinen**.

Das Projekt ist kein bloßer "Chat mit PDF". Im Mittelpunkt steht die Frage, ob struktur-bewusstes Chunking und passende Retriever die richtige **answer-bearing evidence** in halb-strukturierten Modulhandbüchern finden.

## Was das System kann

- PDF-, TXT- und Markdown-Ingestion
- drei Chunking-Strategien: `naive`, `module`, `field`
- BM25, Dense Retrieval und Hybrid Retrieval
- Fragen auf Deutsch, Englisch und Türkisch
- natürlich formulierte Fragen ohne zwingende Modulnummer
- automatische Auswahl des passenden Modulhandbuch-Korpus
- sichtbare Quellen und Evidence-Chunks
- optionale lokale Antwortgenerierung mit Ollama
- Evaluation mit Hit@1, MRR, nDCG@k, Precision@k und Recall@k
- per-query-type-Auswertung
- BM25-Ablation mit und ohne Section-Boosting
- moderne Streamlit-Oberfläche mit abgerundetem Texteingabefeld
- vollständig editierbare PowerPoint-Präsentation

## Natürliche Sprache ohne Modulnummer

Das System kann Fragen wie diese verarbeiten:

```text
Welche Veranstaltung behandelt Information Retrieval?
Welche Module behandeln Suchmaschinen?
Which course covers information retrieval?
Bilgi erişimi ile ilgili hangi ders var?
```

Dafür wird keine Modulnummer benötigt. Die App analysiert die Frage in mehreren Schritten:

1. Sprache erkennen: Deutsch, English oder Türkçe
2. Fragetyp erkennen: Inhalte, Prüfungsform, ECTS, Voraussetzungen, Semester, Verantwortliche oder Unterrichtssprache
3. englische und türkische Begriffe für den lexikalischen Retriever um deutsche Handbuchbegriffe ergänzen
4. bei Bedarf das passende Modulhandbuch automatisch auswählen
5. den Retriever im Auto-Modus wählen

Der Auto-Modus verwendet:

- **BM25**, wenn eine konkrete Modulnummer erkannt wird
- **Hybrid Retrieval**, wenn die Frage frei, semantisch oder mehrsprachig formuliert ist

Wichtig: Das System "versteht" natürliche Sprache nicht wie ein Mensch. Die natürliche Suche entsteht durch Intent-Erkennung, Query Expansion und multilinguale Embeddings. Sehr vage Fragen bleiben schwieriger als klare Themenfragen.

## Automatische Korpuswahl

Im Interface kann das Korpus manuell oder automatisch gewählt werden.

Beispiele:

```text
Master Computerlinguistik
```

führt zum Computerlinguistik-Master-Modulhandbuch.

```text
Informatik Bachelor
```

verwendet standardmäßig das Bachelor-Modulhandbuch mit integriertem Anwendungsfach.

```text
Informatik Bachelor Nebenfach 60 ECTS
```

verwendet die passende Nebenfachvariante.

```text
Informatik Master, Beginn im SoSe
```

verwendet die Sommersemester-Version.

Wenn die Frage keinen Studiengang und keinen Abschluss nennt, durchsucht die App den empfohlenen Demo-Korpus:

- Computerlinguistik Bachelor
- Computerlinguistik Master
- Informatik Bachelor, integriertes Anwendungsfach
- Informatik Master, Beginn WiSe

Die ausgewählten Dokumente werden im Interface immer angezeigt.

## Enthaltene Modulhandbücher

Die offiziellen LMU-PDFs liegen unter `data/raw/`:

```text
lmu_computerlinguistik_bsc_stand_2025-09-24.pdf
lmu_computerlinguistik_msc_stand_2025-07-08.pdf
lmu_informatik_bsc_integriertes_anwendungsfach_stand_2023-11-22.pdf
lmu_informatik_bsc_30ects_nebenfach_stand_2023-11-22.pdf
lmu_informatik_bsc_60ects_nebenfach_stand_2023-11-22.pdf
lmu_informatik_msc_beginn_wise_stand_2023-01-20.pdf
lmu_informatik_msc_beginn_sose_stand_2023-01-20.pdf
```

Die Herkunft der Dokumente ist unter `docs/modulhandbuch_quellen.md` dokumentiert.

## Installation unter Windows und Git Bash

```bash
cd ~/Downloads/suchmaschinen_langer/modulehandbook-rag
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[all]"
```

Nur die Basisversion:

```bash
python -m pip install -e .
```

Dense und Hybrid Retrieval benötigen `sentence-transformers`. Die App benötigt `streamlit`.

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

## Interface starten

```bash
streamlit run app.py
```

Empfohlene Einstellungen für die Demo:

```text
Korpus: Automatisch aus der Frage
Sprache: Auto
Retriever: Auto
Chunk-Datei: data/processed/chunks_field.jsonl
Top-k: 4
Section Boost: 8
Query Expansion: an
```

Die große Suche oben verwendet ein bewusst abgerundetes Texteingabefeld. Die relevanten CSS-Regeln stehen direkt in `app.py` unter dem Kommentar `Abgerundetes Texteingabefeld`.

## Evaluation ausführen

Unter Git Bash:

```bash
bash scripts/run_final_benchmark.sh
```

Unter Windows CMD:

```bat
scripts\run_final_benchmark.bat
```

Aktueller veröffentlichter BM25-Stand mit 25 Queries und `top_k = 3`:

| Chunking | Relevanz | Hit@1 | MRR | nDCG@3 |
|---|---|---:|---:|---:|
| naive | Modul-Level | 0.760 | 0.827 | 0.676 |
| module | Modul-Level | 0.960 | 0.960 | 0.960 |
| field | Modul-Level | 0.840 | 0.873 | 0.512 |
| field | Modul und Section | 0.680 | 0.733 | 0.735 |

Die strikte Field-Evaluation ist für den RAG-Anwendungsfall besonders relevant, weil nicht nur das Modul, sondern auch das richtige Evidenzfeld stimmen muss.

## Präsentation

Die editierbare Präsentation liegt unter:

```text
presentation/modulhandbuch-rag_praesentation_editierbar.pptx
```

Alle Überschriften, Karten, Diagrammbalken, Zahlen und UI-Elemente sind native PowerPoint-Objekte und können bearbeitet werden.

## Terminal wieder hübsch machen

Schnelle Variante ohne Installation:

```bash
bash scripts/setup_terminal_pretty.sh
source ~/.bashrc
```

Starship-Variante unter Windows:

```bash
winget install --id Starship.Starship
bash scripts/setup_terminal_starship.sh
source ~/.bashrc
```

Zurücksetzen:

```bash
bash scripts/restore_terminal_prompt.sh
source ~/.bashrc
```

Details stehen unter `docs/terminal_setup.md`.

## Projektstruktur

```text
modulehandbook-rag/
  app.py
  README.md
  data/
    raw/
    eval/
    processed/
  docs/
  outputs/
  presentation/
  scripts/
  src/modulehandbook_rag/
    query_understanding.py
    handbook_catalog.py
    bm25_retrieval.py
    dense_retrieval.py
    hybrid_retrieval.py
  tests/
```

## Präsentationsclaim

> Explizite Modulnamen helfen, sind aber nicht zwingend nötig. Für natürlich formulierte und mehrsprachige Fragen ist Hybrid Retrieval der robuste Default. Bewertet wird vor allem, ob die richtige belegende Textstelle gefunden wird.

## Einschränkungen

- Die Modulhandbücher sind deutsch. Englisch und Türkisch funktionieren deshalb am besten mit Dense oder Hybrid Retrieval.
- Ohne installierte Dense-Abhängigkeiten fällt die App transparent auf BM25 zurück.
- Sehr allgemeine Fragen können relevante Treffer aus mehreren Modulhandbüchern liefern.
- Section-Boosting ist eine Domain-Heuristik und wird deshalb separat von der BM25-Baseline ausgewiesen.
- Die generative Antwort ist optional. Der methodische Schwerpunkt liegt auf Retrieval und Evidenz.
