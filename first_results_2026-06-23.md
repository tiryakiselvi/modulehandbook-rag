# Erste reproduzierbare Ergebnisse

## Versuchsprotokoll

- Korpus: `cl_bsc_modulhandbuch.pdf`, 36 Seiten, 17 erkannte Module, 307 Feld-Chunks
- Gold-Set: 8 deutsche Fragen, mit Modulkode und Zielabschnitt gelabelt
- Bewertung: **strict section match**, Top-k = 3
- Dense Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Hybrid: Min-Max-Normalisierung über das gesamte Korpus, alpha = 0.5

| Methode | Hit@1 | MRR | nDCG@3 | Recall@3 | Einordnung |
|---|---:|---:|---:|---:|---|
| BM25 (Baseline, Boost 0) | 0.625 | 0.625 | 0.625 | 0.625 | Stark bei exakten Feldbegriffen, WP3-ECTS nur Rang 4. |
| BM25 + field boost 8 | 0.750 | 0.792 | 0.812 | 0.875 | Sinnvolle Heuristik-Ablation, **nicht** die BM25-Baseline. |
| Dense | 0.500 | 0.542 | 0.496 | 0.531 | Gut bei breiten Themenfragen, schwach bei exakten Feldern. |
| Hybrid (alpha 0.5) | 0.625 | 0.708 | 0.717 | 0.781 | Gute Rangqualität/Recall, aber mit alpha 0.5 keine Hit@1-Steigerung gegenüber BM25. |



1. Die Struktur des Dokuments ist informativ: Die explizite Feldheuristik verbessert strukturierte Feldfragen messbar.
2. Der Dense Encoder hilft bei semantischen/breiten Themenfragen: dort erreicht er auf diesem kleinen Set Hit@1 = 1.0, während BM25 und Hybrid je 0.5 erreichen.
3. Für exakte Fragen nach Prüfungsform oder Verantwortlichkeit erreichen BM25 und Hybrid Hit@1 = 1.0; Dense liegt dort bei 0.0.
4. Das ist ein **Pilotresultat**, keine generalisierbare Rangliste: acht manuell gelabelte Fragen reichen nicht für Signifikanztests. Als nächste Stufe erweitern wir das Gold-Set und trennen Entwicklungs- von Testfragen, bevor alpha oder Boost getunt werden.
