# Live-Demo-Runbook

Dieses Runbook ist für die Präsentation im Seminarraum gedacht. Es verwendet die
Chunk-Dateien und Modelle des finalen Release-Laufs.

## 1. Am Vortag

Im Projektordner:

```powershell
cd C:\Users\ASUS\Documents\rag\modulehandbook-rag
.\scripts\prepare_demo_data.ps1 -SourceDirectory "outputs\final_release"
.\.venv\Scripts\python.exe -m pytest -q
ollama list
```

Erwartet:

- `13 passed`
- `llama3.2:3b` ist lokal vorhanden
- `data\processed\chunks_field.jsonl` ist vorhanden
- `data\processed\chunks_module.jsonl` ist vorhanden
- `data\processed\chunks_naive.jsonl` ist vorhanden

## 2. Zehn Minuten vor dem Vortrag

```powershell
cd C:\Users\ASUS\Documents\rag\modulehandbook-rag
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Browser: `http://localhost:8501`

Sidebar einstellen:

- Korpus: `Automatisch aus der Frage`
- Sprache: `Auto`
- Chunk-Datei: `data/processed/chunks_field.jsonl`
- Retriever: `Auto`
- Evidence chunks: `3`
- Section Boost: `8.0`
- Query Expansion: eingeschaltet
- Hybrid Dense-Gewicht: `0.25`
- Antwortmodus: `Ollama LLM answer`
- Ollama-Modell: `llama3.2:3b`

Danach jede der drei Fragen einmal testen und die Seite wieder bis zum Eingabefeld
hochscrollen.

## 3. Reihenfolge im Vortrag

### Anfrage 1 — beantwortbar

```text
Wie viele ECTS hat WP3 im Bachelor Computerlinguistik?
```

Erwartet: `WP3 Information Retrieval umfasst 9 ECTS-Punkte` plus sichtbare Quellen.

### Anfrage 2 — mehrdeutig

```text
Wie viele ECTS hat P1?
```

Erwartet: Bitte um Präzisierung von Studiengang oder Modulhandbuch. Ohne diese Angabe
verwendet die automatische Auswahl das dokumentierte Vier-PDF-Korpus, in dem `P1`
mehrdeutig ist.

### Anfrage 3 — nicht belegt

```text
An welchem Datum findet die nächste Prüfung für WP3 im Bachelor Computerlinguistik statt?
```

Erwartet: `Diese Information ist im bereitgestellten Kontext nicht enthalten.`

## 4. Was während der Demo gesagt wird

- Bei Anfrage 1: „Der exakte Feldwert wird direkt aus der strukturierten Evidenz
  übernommen; darunter bleiben die Fundstellen sichtbar.“
- Bei Anfrage 2: „Das System entscheidet sich gegen eine scheinbar eindeutige Zahl und
  fordert zuerst den fehlenden Kontext an.“
- Bei Anfrage 3: „Die nächste Prüfung steht nicht im Modulhandbuch. Deshalb wird keine
  plausible Terminangabe erzeugt.“

## 5. Fallback ohne Live-Debugging

Wenn die App nicht innerhalb von 20 Sekunden verfügbar ist:

1. Nicht vor der Klasse debuggen.
2. Excel öffnen: `deliverables/Modulhandbuch_RAG_Finalauswertung.xlsx`.
3. Blatt `Dashboard` zeigen.
4. Blatt `Antwortpilot`, Zeilen 4–7 und 15–21 zeigen.
5. Sagen: „Die drei Verhaltensklassen wurden im kontrollierten Pilot mit jeweils drei
   Wiederholungen vorab geprüft; hier sind die gespeicherten Runs.“

## 6. Technischer Hinweis zum Dense-Modell

`HF_HUB_OFFLINE=1` und `TRANSFORMERS_OFFLINE=1` verhindern ausschließlich eine
Versionsabfrage im Netz. Verwendet wird weiterhin der lokal gespeicherte Snapshot von
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; Modellname und Gewichte
ändern sich dadurch nicht.

