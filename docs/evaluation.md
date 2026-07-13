# Evaluation

Die Evaluation misst die Qualität der gefundenen Evidenzstellen vor der optionalen Antwortgenerierung. Dadurch wird geprüft, ob das System die Textstellen findet, auf denen eine korrekte Antwort basieren kann.

## Gold Queries

Die Evaluationsdateien liegen unter `data/eval/`.

- `retrieval_eval_queries.jsonl`: deutschsprachige Retrieval-Fragen
- `multilingual_eval_queries.jsonl`: deutsch-, englisch- und türkischsprachige Varianten

Jede Query enthält eine ID, einen Fragetyp und Goldlabels für die erwartete Antwortstelle.

## Metriken

Verwendete Retrieval-Metriken:

- Hit@1
- MRR
- nDCG@k
- Precision@k
- Recall@k

Optional kann die Evaluation nach Fragetypen gruppiert werden, zum Beispiel Prüfungsform, ECTS, Inhalte oder Sprache.

Relaxed Modul-Retrieval und strict Section-Retrieval sind getrennte Aufgaben. Strict-Ergebnisse für Naive- oder Module-Chunks werden nicht als Qualitätsvergleich berichtet, da diese Chunktypen keine kompatiblen Section-Einheiten besitzen.

Die abschließenden Ergebnisse und ihre methodische Einordnung stehen in [`docs/final_evaluation.md`](final_evaluation.md). Die zugehörigen Rohdateien liegen unter `outputs/final_evaluation/`.

## Beispielbefehle

```bash
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/retrieval_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever bm25 \
  --top-k 3 \
  --require-section \
  --by-query-type
```

```bash
python -m modulehandbook_rag.cli evaluate \
  --eval-file data/eval/multilingual_eval_queries.jsonl \
  --chunks data/processed/chunks_field.jsonl \
  --retriever hybrid \
  --top-k 3 \
  --require-section \
  --by-query-type
```
