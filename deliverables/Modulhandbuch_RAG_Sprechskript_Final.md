# Sprechskript · Modulhandbuch-RAG

Selvinaz Tiryaki · Salem Depebe

Zielzeit: etwa 19 Minuten plus zwei bis drei Minuten Live-Demo

Stand: 14.07.2026 · Release-Commit: `0d3bdc9df033f9823c287b2a7cb7b0c69acc7d64`

Hinweise in eckigen Klammern werden nicht vorgelesen. Sie steuern Folienwechsel,
Excel und Demo. Die Formulierungen sind so geschrieben, dass sie direkt gesprochen
werden können; kurze eigene Abweichungen sind ausdrücklich erlaubt.

## Folie 1 · Titel

**Selvinaz · ca. 55 Sekunden**

[Folie öffnen. Zwei Sekunden warten. Blick ins Publikum.]

Guten Morgen zusammen. Wir sind Selvinaz Tiryaki und Salem Depebe. Unser Projekt heißt
„RAG-basierte Suche in LMU-Modulhandbüchern“.

Die Ausgangsfrage war sehr praktisch: Wie kann man in langen, halbstrukturierten
Modulhandbüchern zuverlässig eine konkrete Information finden – und wie verhindert man,
dass das System aus einem nur ungefähr passenden Treffer eine überzeugend klingende,
aber falsche Antwort macht?

Dafür haben wir sieben Modulhandbücher technisch verarbeitet. Unsere Retrieval-Qualität
messen wir auf 43 manuell kontrollierten Anfragen: 25 deutschen und 18 mehrsprachigen
Anfragen in Deutsch, Englisch und Türkisch.

Die Leitidee unseres Systems steht unten auf der Folie: Retrieval zuerst. Eine Antwort
gibt es nur, wenn wir dafür sichtbare Evidenz haben.

[Weiter zu Folie 2.]

## Folie 2 · Problem und Evidenzkette

**Selvinaz · ca. 55 Sekunden**

Nehmen wir eine scheinbar einfache Frage: „Welche Prüfungsform hat WP3 Information
Retrieval?“ Für einen Menschen klingt das nach einer kurzen Suche. Technisch liegen aber
vier Schritte dazwischen.

Zuerst muss das PDF-Layout lesbar extrahiert werden. Danach muss das System erkennen,
welche Zeilen zu WP3 gehören. Innerhalb dieses Moduls muss es genau den Abschnitt
„Form der Modulprüfung“ treffen. Und am Ende muss es die Seite und die Quelle mitliefern.

Modulhandbücher sind eben keine sauberen Datenbanken. Feldnamen wie ECTS oder
Prüfungsform wiederholen sich in fast jedem Modul. Ein Treffer kann deshalb thematisch
plausibel sein und trotzdem zum falschen Modul oder zum falschen Abschnitt gehören.

[Weiter zu Folie 3.]

## Folie 3 · Fehlerkette

**Selvinaz · ca. 50 Sekunden**

Wir betrachten das als Fehlerkette. Wenn beim Parsing Tabellenzeilen falsch gelesen
werden, arbeitet alles Weitere mit einer schlechten Grundlage. Wenn das Chunking den
Modulkontext verliert, kann Retrieval den richtigen Begriff im falschen Modul finden.
Und wenn Retrieval nur ungefähr stimmt, kann die Antwort zwar flüssig wirken, ist aber
nicht belastbar.

Deshalb trennen wir zwei Fragen, die in RAG-Projekten oft vermischt werden: Erstens, wurde
die richtige Evidenz gefunden? Zweitens, verhält sich das Antwortsystem mit dieser
Evidenz korrekt? Unsere Messlogik lautet darum: erst Retrieval messen, dann Antworten
bewerten.

[Weiter zu Folie 4.]

## Folie 4 · Forschungsfragen

**Selvinaz · ca. 45 Sekunden**

Daraus ergeben sich drei Entscheidungen.

Erstens: Wie schneiden wir die Dokumente? Wir vergleichen naive, modulweite und
feldgenaue Chunks.

Zweitens: Wie suchen wir? Dafür vergleichen wir BM25, Dense Retrieval und verschiedene
Hybrid-Gewichte.

Und drittens: Wann darf das System antworten? Bei eindeutiger Evidenz soll es antworten,
bei Mehrdeutigkeit nachfragen und bei einer nicht belegbaren Information ausdrücklich
zurückhaltend bleiben.

Diese drei Entscheidungen bilden auch die Struktur des restlichen Vortrags.

[Weiter zu Folie 5.]

## Folie 5 · Daten und Geltungsbereich

**Selvinaz · ca. 1 Minute 10 Sekunden**

Hier ist eine methodische Abgrenzung wichtig. Wir haben alle sieben PDFs ingestiert,
segmentiert und in einem Vollkorpus-Stresstest verarbeitet. Damit prüfen wir zum Beispiel,
ob alle Varianten durchlaufen, wie viele Chunks entstehen und ob Chunk-IDs eindeutig
bleiben.

Die offiziellen Qualitätsmetriken beziehen sich aber bewusst nur auf ein Dokument: das
Bachelor-Modulhandbuch Computerlinguistik vom 24. September 2025. Nur dafür besitzen wir
manuell geprüfte Goldlabels auf Dokument-, Modul- und Abschnittsebene.

Auf diesem Goldset liegen 25 deutsche Fragen und 18 mehrsprachige Fragen. Für die anderen
sechs Handbücher erzeugen wir keine künstlichen Qualitätswerte. Eine echte
dokumentübergreifende Qualitätsbewertung würde zusätzliche manuelle Annotationen pro
Handbuch benötigen.

Das heißt kurz: sieben PDFs für technische Robustheit, ein Gold-PDF für belastbare
Retrieval-Qualität.

[Weiter zu Folie 6.]

## Folie 6 · Pipeline

**Selvinaz · ca. 55 Sekunden**

Unsere Pipeline beginnt mit den PDFs. Wir extrahieren den Text, erkennen Module und
wiederkehrende Felder und erzeugen daraus drei Chunking-Varianten. Darauf laufen BM25,
Dense oder Hybrid Retrieval.

Zwischen Retrieval und Antwort liegt eine bewusste Policy. Sie prüft, ob die Anfrage
eindeutig und mit dem gefundenen Kontext belegbar ist. Erst danach entsteht eine Antwort
mit Seite und Quelle.

Parallel speichern wir vier Arten von Evidenz über das System selbst: aggregierte
Retrieval-Metriken, eine Fehleranalyse pro Anfrage, Korpus- und ID-Integrität sowie den
kontrollierten Antwortpilot. Dadurch bleibt sichtbar, an welcher Stufe ein Ergebnis
zustande kommt.

[Weiter zu Folie 7.]

## Folie 7 · Chunking

**Selvinaz · ca. 1 Minute 5 Sekunden**

Beim Chunking vergleichen wir drei Schnitte. Das naive Verfahren arbeitet mit 900
Zeichen und 120 Zeichen Überlappung. Das ist ein nützlicher Baseline-Schnitt, garantiert
aber keine Modul- oder Feldgrenze.

Beim Module Chunking bleibt ein ganzes Modul zusammen. Das erhält viel Kontext und ist
besonders sinnvoll, wenn zuerst das richtige Modul gefunden werden soll.

Beim Field Chunking wird dagegen jedes strukturierte Feld separat gespeichert, zum
Beispiel ECTS, Prüfungsform, Inhalte oder Unterrichtssprache. Dadurch kann das Retrieval
später genau den gefragten Abschnitt treffen.

Unsere wichtigste Einsicht an dieser Stelle ist: Es gibt nicht das eine beste Chunking
für jede Teilaufgabe. Module Chunking beantwortet die Navigationsfrage. Field Chunking
beantwortet die Evidenzfrage.

[Weiter zu Folie 8.]

## Folie 8 · Ergebnis Modulfund

**Selvinaz · ca. 1 Minute 10 Sekunden inklusive Excel**

Zuerst messen wir nur den Modulfund. Dafür gilt ein Treffer als richtig, wenn Dokument
und Modul stimmen; der genaue Abschnitt ist hier noch nicht Teil des Goldschlüssels.

Auf den 25 deutschen Fragen erreicht das naive Chunking mit BM25 64 Prozent Hit@1. Field
Chunking kommt auf 84 Prozent. Module Chunking erreicht 96 Prozent. Bei 24 von 25 Fragen
steht also sofort das richtige Modul oben.

Das passt zur Struktur: Wenn das komplette Modul zusammenbleibt, kann BM25 Modulcode,
Titel und inhaltliche Begriffe gemeinsam nutzen.

[REGIE: Jetzt kurz zu Excel wechseln. Blatt `Ergebnisse`, Zeilen 4–8. Zeile 7 markieren;
Hit@1 und Recall@3 zeigen. Alternativ Dashboard, Zellen A30:C33.]

In der Excel-Datei sehen wir dieselben Werte direkt aus den Rohdaten verknüpft. Es gibt
hier keine manuell eingetippten Ergebniszahlen. Für die Präsentation nehmen wir also 96
Prozent als Antwort auf die Navigationsfrage mit.

[Zur Präsentation zurück. Weiter zu Folie 9.]

## Folie 9 · Modul versus Abschnitt

**Selvinaz · ca. 1 Minute**

Warum reicht das noch nicht? Anfrage q07 fragt nach Modulen zu Informationssuche und
Suchmaschinen. Das System findet WP3 Information Retrieval, also das richtige Modul.
Der erste Feldtreffer ist aber „Qualifikationsziele“. Im Goldset ist der relevante
Abschnitt „Inhalte“, und der erscheint erst auf Rang zwei.

Für die lockere Modulbewertung ist das korrekt. Für eine feldgenaue Antwort ist Rang eins
noch falsch. Dieses Beispiel erklärt, warum wir relaxed und strict getrennt auswerten und
warum ein hoher Modulfund nicht automatisch einen ebenso hohen Feldfund bedeutet.

Damit ist der Chunking-Teil abgeschlossen. Salem zeigt jetzt, wie sich BM25, Dense und
Hybrid in der strengeren feldgenauen Evaluation verhalten.

[Salem übernimmt. Weiter zu Folie 10.]

## Folie 10 · BM25, Dense und Hybrid

**Salem · ca. 1 Minute**

Danke, Selvi. BM25 und Dense liefern zwei unterschiedliche Signale. BM25 reagiert stark
auf exakte Begriffe, Modulcodes und Feldnamen. Dense Retrieval bildet semantische
Ähnlichkeit ab und kann mehrsprachige Formulierungen besser zusammenbringen.

Im Hybrid kombinieren wir beide normalisierten Scores. Wichtig für die Lesart ist: Alpha
ist bei uns der Dense-Anteil. Bei Alpha 0,25 kommen also 25 Prozent des Scores aus Dense
und 75 Prozent aus BM25. Bei Alpha 0,75 ist es umgekehrt.

Diese Definition ist entscheidend für die Interpretation der Ergebnisse: Unser bestes
Hybridmodell enthält mehr lexikalisches als dichtes Signal. Dense ergänzt BM25, es ersetzt
es nicht.

[Weiter zu Folie 11.]

## Folie 11 · Strict und relaxed

**Salem · ca. 55 Sekunden**

Noch einmal präzise zur Bewertungslogik. Bei relaxed lautet der Goldschlüssel Dokument
plus Modul. Das ist die passende Sicht für den Modulfund und den Chunking-Vergleich.

Bei strict lautet der Schlüssel Dokument plus Modul plus Abschnitt. Diese Sicht verwenden
wir für den Retriever-Vergleich, weil eine belegbare Antwort den richtigen Abschnitt
benötigt.

Strukturell ungeeignete Kombinationen zeigen wir nicht als künstliche Nullwerte. Ein
Module Chunk kann zum Beispiel keinen einzelnen Feldabschnitt repräsentieren. Eine 0,000
würde dort wie schlechte Qualität aussehen, obwohl in Wahrheit die Bewertungseinheit
nicht passt.

[Weiter zu Folie 12.]

## Folie 12 · BM25-Ablation

**Salem · ca. 1 Minute 15 Sekunden inklusive Excel**

Bevor wir Retriever vergleichen, zerlegen wir BM25 in seine Beiträge. Ohne Query Expansion
und ohne Section Boost liegen Hit@1 und Recall@3 jeweils bei 28 Prozent.

Mit Query Expansion steigt Hit@1 auf 56 Prozent und Recall@3 auf 80 Prozent. Wir ergänzen
dabei kontrolliert Begriffe wie „Prüfungsform“ oder „Modulprüfung“, damit die Anfrage die
Sprache des Handbuchs besser trifft.

Der Section Boost verbessert anschließend Hit@1 weiter auf 68 Prozent. Recall@3 sinkt
leicht von 80 auf 78 Prozent. Das ist kein Rechenfehler, sondern ein Trade-off: Der Boost
sortiert den gewünschten Feldtyp häufiger auf Rang eins, kann aber einen anderen
relevanten Treffer aus den Top drei verdrängen.

[REGIE: Excel `Ergebnisse`, Zeilen 29–33 öffnen. Erst D31:D33, danach E31:E33 zeigen.]

Insgesamt gewinnen wir gegenüber Plain BM25 40 Prozentpunkte bei Hit@1.

[Zur Präsentation zurück. Weiter zu Folie 13.]

## Folie 13 · Deutsche strict Evaluation

**Salem · ca. 1 Minute 20 Sekunden inklusive Excel**

Jetzt vergleichen wir Dense, BM25 und Hybrid auf denselben 25 deutschen Fragen mit
Field Chunking und strict Matching.

Dense allein erreicht 28 Prozent Hit@1 und 40 Prozent Recall@3. Das domain-angepasste
BM25 liegt deutlich höher: 68 Prozent Hit@1 und 78 Prozent Recall@3.

Hybrid mit Alpha 0,25 erzielt den besten ersten Rang: 72 Prozent Hit@1 und 88 Prozent
Recall@3. Hybrid mit Alpha 0,50 senkt Hit@1 auf 64 Prozent, erreicht dafür den höchsten
Recall@3 von 90 Prozent.

Damit gibt es zwei sinnvolle Betriebsziele. Wenn die erste Evidenzstelle möglichst oft
stimmen soll, wählen wir Alpha 0,25. Wenn eine nachgelagerte Stufe alle Top-3-Treffer
prüfen kann, ist Alpha 0,50 beim Recall leicht besser.

[REGIE: Excel `Ergebnisse`, Zeilen 11–17. Zeilen 15 und 16 vergleichen; bei Bedarf MRR
und nDCG@3 in Spalten F und G zeigen.]

Für unsere Demo und die Hauptinterpretation verwenden wir Alpha 0,25.

[Zur Präsentation zurück. Weiter zu Folie 14.]

## Folie 14 · Mehrsprachiges Design

**Salem · ca. 50 Sekunden**

Für die mehrsprachige Evaluation ändern wir nur die Sprache, nicht die Suchintention.
Sechs Intentionen liegen jeweils auf Deutsch, Englisch und Türkisch vor. Das ergibt 18
Anfragen.

Dokument, Modul und Goldabschnitt bleiben für die drei Sprachversionen identisch. So
prüfen wir tatsächlich Sprachrobustheit und vergleichen nicht zufällig leichtere deutsche
mit schwierigeren türkischen Fragen.

Das Beispiel auf der Folie fragt in allen drei Sprachen nach der Prüfungsform von WP3.
Der Goldschlüssel bleibt WP3 plus „Form der Modulprüfung“.

[Weiter zu Folie 15.]

## Folie 15 · Mehrsprachiges Ergebnis

**Salem · ca. 1 Minute 15 Sekunden inklusive Excel**

Dense allein bleibt auch hier schwach: 22,2 Prozent Hit@1 und 44,4 Prozent Recall@3.
BM25 ist trotz der fremdsprachigen Fragen bereits stark, weil Modulcodes erhalten bleiben
und die Query Expansion deutsche Feld- und Themenbegriffe ergänzt. Es erreicht 66,7
Prozent Hit@1 und 94,4 Prozent Recall@3.

Hybrid mit Alpha 0,25 verbessert beides: 83,3 Prozent Hit@1 und 100 Prozent Recall@3.
Damit liegt bei allen 18 Fragen die relevante Evidenz innerhalb der ersten drei Treffer.

[REGIE: Excel `Ergebnisse`, Zeilen 20–26 öffnen. Zeilen 22 bis 24 zeigen.]

Wegen der kleinen Stichprobe formulieren wir das bewusst als datensatzbezogenen Befund.
Die Aussage ist nicht, dass Hybrid immer 100 Prozent erreicht. Die Aussage ist: Auf
diesen kontrollierten 18 Fragen schließt der moderate Dense-Anteil die letzte Recall-Lücke.

[Zur Präsentation zurück. Weiter zu Folie 16.]

## Folie 16 · Fehleranalyse und Korpusintegrität

**Salem · ca. 1 Minute 20 Sekunden inklusive Excel**

Aggregierte Werte allein erklären noch nicht, was schiefgeht. Deshalb speichern wir für
jede Anfrage die Goldschlüssel, die Top-3-Schlüssel, den ersten relevanten Rang und die
einzelnen Beiträge zu Precision, Recall, MRR und nDCG.

q12 ist ein klarer Fehler: Bei der Prüfungsform von P13 steht P5 oben, und P13 erscheint
nicht in den Top drei. q10 hat zwei relevante Goldfelder, findet aber nur eines davon und
ist deshalb „teilweise“. q07 verfehlt Hit@1, hat den Goldtreffer aber auf Rang zwei und
damit vollständigen Recall@3.

[REGIE: Excel `Fehleranalyse`, Zeilen 16–27. Für die drei Beispiele in den Spalten
Goldmodul, Top-1 Modul, Hit@1, Recall@3 und Status nach rechts scrollen.]

Rechts auf der Folie steht eine andere Art von Prüfung: Im Sieben-PDF-Stresstest entstehen
3.391 Field Chunks und null doppelte Chunk-IDs. Das belegt technische Integrität, aber
keine Qualität auf sechs unannotierten Handbüchern.

[Optional Excel `Korpus`, Zeilen 18–20. Dann zurück zur Präsentation. Weiter zu Folie 17.]

## Folie 17 · Kontrollierter Antwortpilot

**Salem · ca. 1 Minute 15 Sekunden**

Nach dem Retrieval prüfen wir das Antwortverhalten in einem kleinen, kontrollierten
Pilot. Zwei Fragen sind beantwortbar, zwei sind mehrdeutig und zwei verlangen
Informationen, die nicht im Modulhandbuch stehen – konkret ein Prüfungsdatum und eine
E-Mail-Adresse.

Jede Frage läuft dreimal mit Temperatur null und Seed 42. Strukturierte Fakten wie ECTS
werden direkt aus der Feld-Evidenz übernommen. Mehrdeutige Modulcodes führen vor der
Generierung zu einer Rückfrage. Nur bei unbelegbaren Fragen prüft der konservative Prompt,
ob das lokale llama3.2:3b ausdrücklich zurückhält.

In diesem Aufbau sind alle 18 beobachteten Aktionen korrekt, und die drei Antworten pro
Frage sind jeweils exakt identisch.

[REGIE: Excel `Antwortpilot`, Zeilen 4–7 und 15–21 zeigen.]

Wichtig ist die Grenze: Das ist eine Prüfung der Systempolitik, keine umfassende Studie
zur freien Textqualität eines Sprachmodells.

[Zur Präsentation zurück. Weiter zu Folie 18.]

## Folie 18 · Live-Demo

**Salem · ca. 2 bis 3 Minuten**

Wir zeigen jetzt genau diese drei Verhaltensklassen live: zuerst eine belegbare Frage,
dann eine mehrdeutige und am Ende eine nicht belegbare Frage.

[REGIE: Zur bereits geöffneten Streamlit-App wechseln. Einstellungen wurden nach
`docs/LIVE_DEMO_RUNBOOK.md` vorbereitet.]

**Anfrage 1 eingeben:** „Wie viele ECTS hat WP3 im Bachelor Computerlinguistik?“

[Nach dem Ergebnis:]

Hier sehen wir den exakten Wert: WP3 Information Retrieval umfasst 9 ECTS-Punkte. Der
Wert wird direkt aus der strukturierten Field-Evidenz übernommen; darunter bleiben Modul,
Abschnitt und Seite sichtbar.

**Anfrage 2 eingeben:** „Wie viele ECTS hat P1?“

[Nach dem Ergebnis:]

P1 kommt in mehreren ausgewählten Modulhandbüchern vor. Das System nennt deshalb nicht
einfach irgendeine ECTS-Zahl, sondern bittet zuerst um Studiengang oder Modulhandbuch.

**Anfrage 3 eingeben:** „An welchem Datum findet die nächste Prüfung für WP3 im Bachelor
Computerlinguistik statt?“

[Nach dem Ergebnis:]

Ein konkretes Prüfungsdatum steht nicht im Modulhandbuch. Die korrekte Reaktion ist daher:
Diese Information ist im bereitgestellten Kontext nicht enthalten.

[REGIE: Wenn die App nicht innerhalb von 20 Sekunden reagiert, nicht debuggen. Excel
`Antwortpilot` zeigen und den Fallback-Satz aus dem Live-Demo-Runbook verwenden. Danach
zur Präsentation zurück und zu Folie 19 wechseln.]

## Folie 19 · Fazit

**Salem und Selvinaz · ca. 1 Minute 10 Sekunden**

**Salem:** Unsere drei belastbaren Befunde sind: Structure-aware Chunking ist der naiven
Baseline klar überlegen. Hybrid mit Alpha 0,25 liefert die beste Rang-1-Qualität. Und
BM25 trägt wesentlich zu diesem Hybrid bei; Dense allein ist nicht der Leistungstreiber.

Die Grenzen sind genauso wichtig. Das Qualitäts-Gold umfasst bisher ein Modulhandbuch.
Die mehrsprachige Evaluation hat 18 Fragen. Und der Antwortpilot untersucht sechs
kontrollierte Fälle, keine offene Generationsqualität.

Als nächste Schritte würden wir Goldlabels für die übrigen Handbücher erstellen,
Reranking oder Late Chunking wirklich evaluieren und einen persistenten Faktenindex für
exakte Felder prüfen.

**Selvinaz:** Unsere Kernidee bleibt damit sehr einfach: Retrieval entscheidet, was das
System wissen darf. Vielen Dank. Wir freuen uns auf Ihre Fragen.

[Hauptteil endet. Folien 20 und 21 nur bei Fragen öffnen.]

## Folie 20 · Anhang: Metriken

**Salem · nur bei Nachfrage**

Hit@1 prüft, ob der erste Treffer relevant ist. Recall@3 misst, wie viel vom gesamten Gold
in den ersten drei Treffern liegt. MRR bewertet, wie früh der erste relevante Treffer
erscheint. nDCG@3 betrachtet zusätzlich die Qualität der gesamten Top-3-Reihenfolge.

Alle vier Werte werden aus denselben Per-Query-Goldschlüsseln aggregiert. Deshalb können
wir von der Gesamttabelle jederzeit zurück zu einer konkreten Anfrage gehen.

## Folie 21 · Anhang: Reproduktion

**Selvinaz · nur bei Nachfrage**

Der komplette Abgabelauf startet mit einem PowerShell-Befehl. Die Ergebnisse gehören zum
Commit 0d3bdc9. Dreizehn automatisierte Tests bestehen, die 3.391 Field Chunks haben
keine doppelten IDs, und 172 Per-Query-Zeilen bilden die Aggregation nach.

Das Dense-Modell stammt aus demselben lokal gespeicherten Hugging-Face-Snapshot. Die
Offline-Variablen verhindern nur die Netzabfrage; sie ändern weder Modellname noch
Gewichte. Die genaue Anleitung und die Datei-Hashes stehen im Test-Runbook und im
Excel-Blatt `Reproduktion`, Zeilen 4–12 und 32–36.
