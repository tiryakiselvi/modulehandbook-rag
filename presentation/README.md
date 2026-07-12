# Präsentation

Datei:

```text
modulhandbuch-rag_praesentation_editierbar.pptx
```

Die Präsentation wurde vollständig mit nativen PowerPoint-Objekten aufgebaut:

- Texte sind editierbar
- Karten und Flächen sind editierbar
- Farben und Schatten sind editierbar
- Diagrammbalken sind einzelne Formen
- das Interface-Mockup besteht aus editierbaren Formen
- das Suchfeld ist als abgerundetes PowerPoint-Objekt umgesetzt

Die Präsentation verwendet ein helles, reduziertes Design mit weißen Flächen, weichen Blau- und Lilatönen und großzügigem Weißraum.

Die Datei `build_presentation.js` enthält außerdem den PptxGenJS-Quellcode. Damit kann die Präsentation reproduzierbar neu erzeugt werden:

```bash
node presentation/build_presentation.js
```

Der Ausgabe-Pfad im Skript ist auf den GitHub-Ready-Ordner gesetzt. Bei Nutzung direkt im eigenen Repo kann der letzte `writeFile`-Pfad auf einen relativen Pfad angepasst werden.
