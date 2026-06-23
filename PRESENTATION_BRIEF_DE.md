# Präsentation: RAG-Suche in LMU-Modulhandbüchern

## Folie 1 – Problem und Forschungsfrage

**Titel:** *Wie beeinflussen Chunking und Retrieval die Suche in semi-strukturierten Modulhandbüchern?*

Satz dazu: „Wir bauen keinen allgemeinen PDF-Chat. Wir untersuchen, wie ein Retriever die passende belegbare Modulhandbuchstelle findet.“

## Folie 2 – Daten und Herausforderung

- Pilotkorpus: Bachelor-Modulhandbuch Computerlinguistik (36 Seiten)
- 17 erkannte Module, wiederkehrende Felder wie ECTS, Prüfungsform und Inhalte
- Kurzfelder verlangen Präzision; Inhalte und Themenfragen verlangen semantische Abdeckung

## Folie 3 – Pipeline

`PDF -> Bereinigung -> Chunks -> BM25 / Dense / Hybrid -> Quellen -> optionale LLM-Antwort`

Betont: Retrieval wird vor der LLM-Antwort evaluiert. Ohne richtigen Kontext ist eine schöne Antwort nicht verlässlich.

## Folie 4 – Chunking

- Naive Chunks: feste Textfenster, Baseline
- Modul-Chunks: ein ganzer Modulblock, robuster Kontext
- Feld-Chunks: z. B. „Inhalte“ oder „Form der Modulprüfung“, präzise Quellen

Zeigt eure bisherige Tabelle als qualitative Fehleranalyse, nicht als gepoolte Metrik.

## Folie 5 – Faire Hauptevaluation

- Feld-Chunks als eingefrorenes Korpus
- 8 gelabelte deutsche Fragen: factual, numerical, semester, content, broad topic
- Strikte Relevanz: richtiger Modulcode **und** richtiger Abschnitt
- Metriken: Hit@1, MRR, nDCG@3, Recall@3

## Folie 6 – Ergebnisse

| Methode | Hit@1 | MRR | nDCG@3 |
|---|---:|---:|---:|
| BM25 Baseline | .625 | .625 | .625 |
| BM25 + Feldheuristik | .750 | .792 | .812 |
| Dense | .500 | .542 | .496 |
| Hybrid (alpha=.5) | .625 | .708 | .717 |

Sprecht die Probegröße offen aus: Das sind Pilotwerte aus acht Fragen, keine Signifikanzbehauptung.

## Folie 7 – Interpretation mit zwei Gegenbeispielen

1. Exakte WP3-ECTS-/Prüfungsfragen: lexikalische Treffer und Feldinformation helfen BM25.
2. „Welche Module behandeln Informationssuche?“: Dense Retrieval findet semantisch verwandte Inhalte besser.

Die Pointe: Kein Retriever dominiert jede Frage. Struktur, Fragetyp und Methode interagieren.

## Folie 8 – Live-Demo

1. `search` mit einer geprüften Feldfrage und Quelle anzeigen.
2. Dasselbe mit `ask-llm` nach der Ollama-Installation zeigen.
3. Sagen: „Die LLM-Antwort ist eine kontrollierte Präsentationsschicht; die Quellen bleiben sichtbar.“

## Folie 9 – Grenzen und nächste Schritte

- Gold-Set auf mindestens 20–30 Fragen und Master-Handbuch erweitern
- Test- und Entwicklungsfragen trennen, bevor alpha/Boost getunt werden
- Für einen strikten Chunkingvergleich Gold-Evidenzspannen je Chunking-Strategie labeln
- Prüfungsordnungen/Studienpläne als eigenen Dokumenttyp evaluieren
- Multilingual erst als separates Experiment: gleiche Gold-Quelle, Query-Sprache variieren, Antwortsprache getrennt bewerten
