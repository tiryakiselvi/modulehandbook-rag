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
