# Abschließende Evaluation

## Versuchsaufbau

Die Evaluation trennt zwei unterschiedliche Aufgaben:

1. **Modul-Retrieval:** Das richtige Modul muss gefunden werden. Diese Aufgabe ist für Naive-, Module- und Field-Chunking vergleichbar.
2. **Section-Retrieval:** Das richtige Modul und der richtige Abschnitt müssen gefunden werden. Diese Aufgabe wird nur mit Field-Chunks ausgewertet, weil nur diese Strategie konkrete Abschnittsmetadaten erzeugt.

Die offiziellen Retrieval-Metriken verwenden 25 deutsche Goldfragen zum Bachelor-Handbuch Computerlinguistik. Die mehrsprachige Evaluation umfasst dieselben sechs Fragetypen auf Deutsch, Englisch und Türkisch (`n = 18`). Alle Systeme werden mit `top-k = 3` verglichen.

Zusätzlich werden zwei größere Korpora als Robustheitsprüfung verwendet:

- **Kuratierter Hauptkorpus:** je eine klar definierte Version für Computerlinguistik Bachelor, Computerlinguistik Master, Informatik Bachelor und Informatik Master.
- **Varianten-Stresstest:** alle sieben PDFs einschließlich ähnlicher Nebenfach- und Semesterbeginn-Varianten.

Die Robustheitswerte verwenden weiterhin die CL-BSc-Goldfragen. Sie sind daher keine offizielle Qualitätsbewertung der übrigen Studiengänge.

## Chunk-Integrität

| Korpus | Dokumente | Naive | Module | Field | Doppelte Chunk-IDs |
|---|---:|---:|---:|---:|---:|
| CL-BSc offiziell | 1 | 62 | 17 | 307 | 0 |
| Kuratierter Hauptkorpus | 4 | 578 | 146 | 1.990 | 0 |
| Varianten-Stresstest | 7 | 937 | 239 | 3.391 | 0 |

Wiederholte Module und Abschnitte erhalten stabile Part-Indizes. Dadurch wird kein Chunk beim Speichern in Dictionaries oder Vektorindizes überschrieben.

## Chunking-Vergleich: Modul-Retrieval

| Chunking | Hit@1 | Recall@3 | MRR | nDCG@3 |
|---|---:|---:|---:|---:|
| Naive | 0,640 | 0,920 | 0,767 | 0,806 |
| Module | **0,960** | **0,960** | **0,960** | **0,960** |
| Field | 0,840 | 0,920 | 0,873 | 0,885 |

Module-Chunking ist für die Aufgabe „richtiges Modul finden“ am stärksten. Daraus folgt keine generelle Überlegenheit für abschnittsgenaue Evidenz, weil diese Aufgabe separat gemessen wird.

## Retriever-Vergleich: deutsches Section-Retrieval

| Retriever | Alpha | Hit@1 | Recall@3 | MRR | nDCG@3 |
|---|---:|---:|---:|---:|---:|
| BM25 mit Expansion und Section Boost | – | 0,680 | 0,780 | 0,733 | 0,735 |
| Dense | – | 0,280 | 0,400 | 0,340 | 0,353 |
| Hybrid | 0,25 | **0,720** | 0,880 | **0,813** | **0,823** |
| Hybrid | 0,50 | 0,640 | **0,900** | 0,760 | 0,796 |
| Hybrid | 0,75 | 0,320 | 0,640 | 0,473 | 0,519 |

Hybrid `alpha = 0,25` liefert die beste Rangqualität. `alpha = 0,50` erreicht den höchsten Recall@3. Ein hoher Dense-Anteil verschlechtert das Ergebnis auf diesem kleinen, stark strukturierten Korpus. Bei exakt gleichen Fusionsscores entscheidet die Chunk-ID als stabiler zweiter Sortierschlüssel; damit ist die Rangfolge auch über getrennte Python-Prozesse reproduzierbar.

## BM25-Ablation

| Einstellung | Hit@1 | Recall@3 | MRR | nDCG@3 |
|---|---:|---:|---:|---:|
| BM25 ohne Expansion und Boost | 0,280 | 0,280 | 0,300 | 0,274 |
| BM25 mit Expansion, ohne Boost | 0,560 | **0,800** | 0,687 | 0,701 |
| BM25 mit Expansion und Boost | **0,680** | 0,780 | **0,733** | **0,735** |

Query Expansion erzeugt den größten Gewinn. Der Section Boost verbessert die Platzierung des ersten korrekten Treffers, während Recall@3 geringfügig von 0,800 auf 0,780 sinkt.

## Mehrsprachiger Vergleich

| Retriever | Alpha | Hit@1 | Recall@3 | MRR | nDCG@3 |
|---|---:|---:|---:|---:|---:|
| BM25 mit mehrsprachiger Expansion | – | 0,667 | 0,944 | 0,778 | 0,820 |
| Dense | – | 0,222 | 0,444 | 0,315 | 0,348 |
| Hybrid | 0,25 | **0,833** | **1,000** | **0,898** | **0,924** |
| Hybrid | 0,50 | **0,833** | 0,944 | 0,889 | 0,903 |
| Hybrid | 0,75 | 0,278 | 0,778 | 0,519 | 0,586 |

Der Vergleich enthält BM25, Dense und Hybrid auf exakt denselben 18 Fragen. Hybrid `alpha = 0,25` verbessert alle gezeigten Metriken gegenüber BM25. Dense allein bleibt deutlich schwächer; sein Beitrag ist in Kombination mit einer starken lexikalischen Komponente dennoch nützlich.

## Korpus-Robustheit

BM25 mit Field-Chunking erreicht im kuratierten Vier-Dokument-Korpus Recall@3 `0,700` und Hit@1 `0,600`. Im Sieben-Dokument-Stresstest liegen die Werte bei Recall@3 `0,740` und Hit@1 `0,560`. Ähnliche Handbuchvarianten verändern damit vor allem die Rangfolge. Der kuratierte Korpus ist die geeignete Hauptkonfiguration; alle Varianten bilden einen separaten Stresstest.

## Antwortverhalten und Reproduzierbarkeit

Ein Pilotset enthält zwei beantwortbare, zwei nicht belegte und zwei mehrdeutige Fragen. Jede Frage wurde mit `llama3.2:3b`, Temperatur `0` und Seed `42` dreimal ausgeführt (`18` Ausgaben).

- Beantwortbare strukturierte Felder werden deterministisch aus der belegten Field-Evidenz übernommen.
- Nicht belegte Angaben werden abgelehnt.
- Wenn derselbe Modulcode in mehreren Handbüchern vorkommt, wird vor der Generierung eine Rückfrage gestellt.
- Im Pilot betrugen Verhaltensgenauigkeit und exakte Reproduzierbarkeit jeweils `1,000`.

Der Pilot belegt das Verhalten nur für sechs kontrollierte Fragen. Er ersetzt keine größere End-to-End-Studie.

## Grenzen und weitere Arbeit

- Die offiziellen Goldlabels decken derzeit ein Handbuch ab.
- 25 beziehungsweise 18 Fragen erlauben keine weitreichende statistische Generalisierung.
- Late-Chunking ist nicht Bestandteil der aktuellen Pipeline. Die Metadatenzuordnung erfolgt deterministisch über Modul- und Abschnittsgrenzen; Late-Chunking wäre eine zusätzliche Embedding-Ablation.
- Exakte Felder werden bereits strukturiert aus Field-Chunks aufgelöst. Ein separater persistenter Faktenindex wäre eine weiterführende Erweiterung.

Die vollständigen Rohwerte, Fragetyp-Auswertungen, Per-Query-Fehleranalyse und Integritätsprüfung des Abgabelaufs liegen unter `outputs/final_release/`.
