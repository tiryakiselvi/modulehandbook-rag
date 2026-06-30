
Kurs  : Masterseminar Suchmaschinen, Retrieval Augmented Generation und Agentensysteme
Gruppe: Selvinaz Tiryaki und Salem Debebe

Dieses Projekt untersucht, wie unterschiedliche Chunking-Strategien und Suchverfahren die Qualität der Belegsuche in LMU-Modulhandbüchern beeinflussen. Im Mittelpunkt stehen Fragen zu ECTS-Punkten, Prüfungsformen, Modulbeschreibungen, Studienplänen und relevanten Ordnungsdokumenten.

## Projektiel
Modulhandbücher sind halbstrukturierte Dokumente: kurze Felder wie ECTS, Sprache oder Prüfungsform stehen neben längeren Beschreibungen. Deshalb wird verglichen, ob feldnahe Chunks, modulweite Chunks oder feste Textfenster für verschiedene Fragetypen bessere Treffer liefern.

## Pipeline

```text
PDF-Dokumente
        -> Textextraktion und Bereinigung
        -> Chunking (naive | module | field)
        -> Suche (bm25 | dense | hybrid)
        -> Ranking und Belege
        -> Auswertung mit festen Testfragen
```

## Wichtige Dateien

```text
src/modulehandbook_rag/          Programmcode und CLI
data/raw/                        Quell-PDFs
data/processed/                  erzeugte Chunk-Dateien
data/eval/                       gelabelte Testfragen
outputs/                         neu erzeugte Ergebnisdateien
RUNBOOK_DE.md                    kurzer Startpunkt
..\test_runbook.md               vollständiges Test-Runbook
..\test_runbook.docx             Word-Version des Test-Runbooks
```

## Start
Alle finalen Testbefehle stehen in:

```text
C:\Users\ASUS\Documents\selviss\selvis2\test_runbook.md
C:\Users\ASUS\Documents\selviss\selvis2\test_runbook.docx
```

Kanonischer Projektordner:

```bat
cd C:\Users\ASUS\Documents\selviss\selvis2\modulehandbook-rag
```

Danach die Befehle aus dem Test-Runbook in CMD ausführen. Für Codeerklärungen können die Dateien in `src/modulehandbook_rag` in Spyder geöffnet werden.
