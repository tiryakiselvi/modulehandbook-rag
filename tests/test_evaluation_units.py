from modulehandbook_rag.evaluation import EvalQuery, evaluate_per_query, evaluate_results
from modulehandbook_rag.schemas import Chunk, SearchResult


def _chunk(chunk_id: str, section: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id="handbook.pdf",
        title="handbook.pdf",
        source_path="handbook.pdf",
        text=section,
        module_code="WP3",
        module_title="Information Retrieval",
        section=section,
    )


def test_module_and_section_metrics_use_gold_units_not_chunk_count():
    chunks = [
        _chunk("content:part:0", "Inhalte"),
        _chunk("content:part:1", "Inhalte"),
        _chunk("exam:part:0", "Form der Modulprüfung"),
    ]
    query = EvalQuery(
        query="Welche Inhalte behandelt WP3?",
        relevant_documents={"handbook.pdf"},
        relevant_modules={"WP3"},
        relevant_sections={"Inhalte"},
    )

    def search(_query: str, _k: int) -> list[SearchResult]:
        return [
            SearchResult(chunks[0], 3.0, 1),
            SearchResult(chunks[1], 2.0, 2),
            SearchResult(chunks[2], 1.0, 3),
        ]

    relaxed = evaluate_results([query], search, chunks, k=3, require_section=False)
    strict = evaluate_results([query], search, chunks, k=3, require_section=True)

    assert relaxed["recall@3"] == 1.0
    assert strict["recall@3"] == 1.0
    assert strict["hit@1"] == 1.0

    detail = evaluate_per_query([query], search, k=3, require_section=True)[0]
    assert detail["relevant_total"] == 1
    assert detail["relevant_found@3"] == 1
    assert detail["recall@3"] == strict["recall@3"]
    assert detail["reciprocal_rank"] == strict["mrr"]
    assert detail["ndcg@3"] == strict["ndcg@3"]
    assert detail["hit@1"] == strict["hit@1"]
    assert detail["result"] == "vollständig"


def test_per_query_row_marks_partial_coverage_of_multiple_gold_sections():
    chunks = [
        _chunk("content:part:0", "Inhalte"),
        _chunk("content:part:1", "Inhalte"),
        _chunk("prerequisite:part:0", "Teilnahmevoraussetzungen"),
    ]
    query = EvalQuery(
        query="Welche Inhalte und Prüfungsform hat WP3?",
        relevant_documents={"handbook.pdf"},
        relevant_modules={"WP3"},
        relevant_sections={"Inhalte", "Form der Modulprüfung"},
    )

    def search(_query: str, _k: int) -> list[SearchResult]:
        return [
            SearchResult(chunks[0], 3.0, 1),
            SearchResult(chunks[1], 2.0, 2),
            SearchResult(chunks[2], 1.0, 3),
        ]

    aggregate = evaluate_results([query], search, chunks, k=3, require_section=True)
    detail = evaluate_per_query([query], search, k=3, require_section=True)[0]

    assert detail["relevant_total"] == 2
    assert detail["relevant_found@3"] == 1
    assert detail["recall@3"] == 0.5
    assert detail["recall@3"] == aggregate["recall@3"]
    assert detail["result"] == "teilweise"
