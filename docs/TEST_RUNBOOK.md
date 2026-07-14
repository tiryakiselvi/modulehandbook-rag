# Test- und Reproduktions-Runbook

## Zweck

Dieses Runbook erzeugt den dokumentierten Abgabestand aus dem Repository neu. Es prüft zuerst den Code, erstellt danach alle Retrieval- und Korpusdateien, führt den kontrollierten Antwortpilot aus und stellt zuletzt die geprüften Vollkorpus-Chunks für die lokale Demo bereit. Die Evaluation verwendet ausschließlich lokale PDF-, Modell- und Ollama-Dateien.

## Geltungsbereich

- Offizielle Qualitätsmetriken: CL-Bachelor-Modulhandbuch, 25 deutsche und 18 mehrsprachige Goldfragen.
- Vier-Dokument-Korpus und alle sieben PDFs: Robustheits- und Integritätsprüfung, keine eigenständige Qualitätsbewertung weiterer Studiengänge.
- Antwortpilot: sechs kontrollierte Fragen mit je drei Wiederholungen; keine umfassende Bewertung freier LLM-Antworten.

## Einmalige Vorbereitung

Im Repository-Stammverzeichnis:

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-release.txt
& .\.venv\Scripts\python.exe -m pip install -e .
```

Vor dem ersten Offline-Lauf müssen diese Modelle einmal lokal vorhanden sein:

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- `llama3.2:3b` in Ollama

Prüfung:

```powershell
ollama list
```

## Vollständiger Abgabelauf

```powershell
& .\scripts\run_release_validation.ps1 -OutputDirectory "outputs\final_release"
```

Erwartete Laufzeit auf dem Abgaberechner: ungefähr zwei Minuten. Der Dense-Teil lädt das Embedding-Modell aus dem lokalen Hugging-Face-Cache. `HF_HUB_OFFLINE=1` und `TRANSFORMERS_OFFLINE=1` verhindern Netzabhängigkeit; sie verändern weder Modell noch Gewichte.

## Erwartete Prüfresultate

- `13 passed`
- 0 doppelte Chunk-IDs in allen neun Corpus-/Chunking-Kombinationen
- 3.391 eindeutige Field-Chunks im Sieben-PDF-Stresstest
- Antwortpilot: Verhaltensgenauigkeit `1,000`, exakte Reproduzierbarkeit `1,000`

Zentrale Retrievalwerte:

| Versuchsblock | Konfiguration | Hit@1 | Recall@3 |
|---|---|---:|---:|
| Modulfund, Deutsch n=25 | Module + BM25 | 0,960 | 0,960 |
| Strict, Deutsch n=25 | Hybrid, α=0,25 | 0,720 | 0,880 |
| Strict, Deutsch n=25 | Hybrid, α=0,50 | 0,640 | 0,900 |
| Strict, mehrsprachig n=18 | Hybrid, α=0,25 | 0,833 | 1,000 |
| Strict, mehrsprachig n=18 | BM25 | 0,667 | 0,944 |

## Erzeugte Dateien

`outputs/final_release/` enthält:

- `retrieval_metrics.csv`: alle Haupt- und Ablationsmetriken
- `query_type_metrics.csv`: Auswertung nach Fragetyp
- `per_query_analysis.csv`: Fehleranalyse je Anfrage und System
- `chunk_integrity.csv`: Dokument-, Chunk- und ID-Prüfung
- `metadata.json`: Commit, Python-Version, Modell und Korpora
- `chunks/`: neun reproduzierte Chunk-Dateien
- `llm_behavior/`: 18 Pilotausgaben und Zusammenfassung

Zusätzlich werden für die Streamlit-Demo aus denselben Release-Chunks erzeugt:

- `data/processed/chunks_field.jsonl`
- `data/processed/chunks_module.jsonl`
- `data/processed/chunks_naive.jsonl`
- `data/processed/chunks.jsonl` als kompatibler Field-Standard

## Schnelle Validierung ohne Ollama

```powershell
& .\scripts\run_release_validation.ps1 `
    -OutputDirectory "outputs\retrieval_only_check" `
    -SkipLlmPilot
```

## Fehlerbehebung

**Dense-Modell nicht im Cache:** Den Rechner einmal mit Internetzugang verbinden und das Modell über einen normalen Hybrid-Lauf laden. Danach den Abgabelauf erneut offline starten.

**Ollama nicht erreichbar:** Ollama starten, `ollama list` ausführen und prüfen, ob `llama3.2:3b` vorhanden ist.

**Abweichende Rangfolge bei Gleichstand:** Der finale Code verwendet bei identischen Hybrid-Scores die Chunk-ID als stabilen zweiten Sortierschlüssel. Fehlt dieser Stand, ist nicht der dokumentierte Release-Commit ausgecheckt.

**Andere Metriken:** Zuerst `metadata.json`, Git-Commit, Python `3.11.9`, `requirements-release.txt` und die PDF-Dateinamen unter `data/raw/` vergleichen. Keine Werte manuell in Excel oder PowerPoint übertragen; beide Artefakte werden aus den Release-CSV-Dateien aufgebaut.
