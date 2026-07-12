# Natürliche Sprachsuche

## Ziel

Nutzer:innen sollen Fragen stellen können, ohne Modulcode oder exakten Modultitel zu kennen.

Beispiele:

```text
Welche Veranstaltung behandelt Information Retrieval?
Welche Module behandeln Suchmaschinen?
Which course covers information retrieval?
Bilgi erişimi ile ilgili hangi ders var?
```

## Technische Umsetzung

Die Datei `src/modulehandbook_rag/query_understanding.py` erzeugt eine strukturierte Analyse der Frage:

- Sprache
- Fragetyp oder Intent
- Studiengang
- Bachelor oder Master
- Varianten wie Nebenfach 30 ECTS, Nebenfach 60 ECTS, SoSe oder WiSe
- vorhandene Modulnummer
- erweiterte BM25-Query

Für BM25 werden englische und türkische Fragetypen auf deutsche Feldbegriffe erweitert. Beispiele:

```text
exam type -> Form der Modulprüfung
credits -> ECTS / Leistungspunkte
prerequisite -> Teilnahmevoraussetzung
teaching language -> Unterrichtssprache
bilgi erişimi -> Information Retrieval / Suchmaschinen
```

Dense Retrieval erhält weiterhin die ursprüngliche Frage. Hybrid Retrieval kombiniert deshalb:

- den Originaltext für die semantische Suche
- die deutsche Erweiterung für die lexikalische Suche

## Auto-Retriever

- Modulnummer vorhanden: BM25
- keine Modulnummer oder nicht-deutsche Frage: Hybrid

Falls Dense Retrieval nicht installiert ist, zeigt die App einen Hinweis und fällt auf BM25 zurück.

## Automatische Dokumentauswahl

Die Query-Analyse kann das Korpus aus der Frage ableiten:

```text
Master Computerlinguistik -> cl_msc
Informatik Bachelor -> inf_bsc_integrated
Nebenfach 60 ECTS -> inf_bsc_minor_60
Informatik Master SoSe -> inf_msc_sose
```

Ohne solche Angaben wird der empfohlene Demo-Korpus verwendet.

## Ehrliche Formulierung für die Präsentation

> Das System benötigt nicht zwingend Modulnummern. Natürliche Fragen werden über Intent-Erkennung, Query Expansion und multilinguale Embeddings mit den deutschen Modulhandbuchtexten abgeglichen.

Nicht behaupten:

```text
Das System versteht jede natürliche Frage perfekt.
```
