# Interface Design

Die Streamlit-App ist als einfache Oberfläche für die Suche in Modulhandbüchern umgesetzt. Sie stellt Korpusauswahl, Sprache, Retriever, Ranking-Parameter und gefundene Evidenzstellen transparent dar.

Zentrale UI-Elemente:

- Auswahl des Korpus
- Auswahl von Sprache und Retriever
- Texteingabe für die Frage
- Anzeige der gefundenen Chunks mit Rang, Score, Modul, Abschnitt und Quelle
- optionale Antwortgenerierung über ein lokales LLM

Das Texteingabefeld ist in `app.py` per CSS abgerundet gestaltet.
