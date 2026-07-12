# Interface Design

Ziel: modern, hell, clean und leicht verspielt, ähnlich einer hellen Keynote-Produktdemo.

## Designprinzipien

- viel Weißraum
- helle Blue/Lilac-Akzente
- abgerundete Cards
- pill-shaped Controls
- transparent sichtbare Evidenz
- keine überladene Dashboard-Optik

## Abgerundetes Texteingabefeld

Das Texteingabefeld wird per CSS gezielt abgerundet:

```css
.stTextInput input {
  border-radius: 999px !important;
  padding: 0.9rem 1.2rem !important;
}
```

Dadurch wirkt die Eingabe wie ein modernes Suchfeld statt wie ein Standardformular.

## Demo-UI

Die App zeigt:

- Sprachwahl: Deutsch, English, Türkçe
- Korpuswahl: Recommended, einzelne Handbücher, alle Handbücher, Custom
- Retriever: BM25, Dense, Hybrid
- Top-k
- Section Boost
- Query Expansion
- Evidenzkarten mit Rank, Score, Modul, Section und Quelle
