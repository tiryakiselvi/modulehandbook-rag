# Übergabe an Salem

Verwende diese Dateien als einzige Präsentationsquelle:

1. `Modulhandbuch_RAG_Finalpraesentation.pptx`
2. `Modulhandbuch_RAG_Finalauswertung.xlsx`
3. `Modulhandbuch_RAG_Sprechskript_Final.docx`
4. `../docs/LIVE_DEMO_RUNBOOK.md`
5. `../docs/TEST_RUNBOOK.md`

Die alten Dateien aus `archive/salem_draft` sind nur Archiv und dürfen nicht mehr als
Zahlenquelle verwendet werden.

## Aufgabenverteilung

- Selvinaz: Folien 1–9; Abschluss-Satz auf Folie 19; Reproduktion bei Nachfrage
- Salem: Folien 10–19; Live-Demo; Metriken bei Nachfrage
- Folien 20–21: Anhang, nicht im normalen Ablauf

## Excel-Wechsel

| Folie | Blatt | Bereich | Punkt |
|---|---|---|---|
| 8 | Ergebnisse | Zeilen 4–8 | Module Chunking: Hit@1 0,960 |
| 12 | Ergebnisse | Zeilen 29–33 | BM25-Ablation; Hit@1 versus Recall@3 |
| 13 | Ergebnisse | Zeilen 11–17 | Hybrid α=0,25 versus α=0,50 |
| 15 | Ergebnisse | Zeilen 20–26 | mehrsprachige Retriever |
| 16 | Fehleranalyse | Zeilen 16–27 | q12, q10, q07; Hit@1 und Recall gemeinsam lesen |
| 16 | Korpus | Zeilen 18–20 | sieben PDFs, 3.391 Field Chunks, null Duplikate |
| 17 | Antwortpilot | Zeilen 4–7 und 15–21 | sechs Fragen, 18 Runs |
| 21 | Reproduktion | Zeilen 4–12 und 32–36 | Commit, Hashes, Befehl, Offline-Hinweis |

## Zahlen, die nicht verändert werden dürfen

- Module Chunking + BM25, Modulfund: Hit@1 = 0,960
- Deutsch strict, Hybrid α=0,25: Hit@1 = 0,720; Recall@3 = 0,880
- Deutsch strict, Hybrid α=0,50: Hit@1 = 0,640; Recall@3 = 0,900
- Mehrsprachig strict, Hybrid α=0,25: Hit@1 = 0,833; Recall@3 = 1,000
- Mehrsprachig strict, BM25: Hit@1 = 0,667; Recall@3 = 0,944
- Stresstest: 7 PDFs; 3.391 Field Chunks; 0 doppelte IDs
- Antwortpilot: 6 Fragen × 3; 100% Verhaltensrichtigkeit; 100% exakte Reproduzierbarkeit
- Tests: 13/13

## Formulierungen

- `α` immer als Dense-Anteil erklären.
- Nicht sagen, Dense sei generell schlecht; korrekt ist: auf diesem Datensatz allein
  schwächer.
- Nicht sagen, alle sieben PDFs seien qualitätsbewertet. Sie sind technisch verarbeitet;
  das Goldset gilt für CL Bachelor.
- Den 6×3-Pilot nicht als allgemeine LLM-Evaluation bezeichnen.
- Late Chunking und Faktenindex nur als nächste Schritte nennen.
- Naive Chunking: 900 Zeichen, 120 Zeichen Überlappung.

## Wenn Salem das Design noch anpasst

Texte, Zahlen, Folienreihenfolge und Auditpfade nicht ändern. Erlaubt sind nur kleine
typografische Anpassungen, sofern danach jede Folie erneut geöffnet und auf Überlauf
geprüft wird. Die vier Ergebnisgrafiken müssen editierbar bleiben; keine Screenshots aus
Excel einsetzen.
