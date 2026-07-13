from modulehandbook_rag.rag import (
    build_rag_prompt,
    clarification_needed,
    structured_field_answer,
)
from modulehandbook_rag.schemas import Chunk, SearchResult


def test_prompt_defines_answer_and_abstention():
    prompt = build_rag_prompt("Wie viele ECTS hat P1?", [])
    assert "Diese Information ist im bereitgestellten Kontext nicht enthalten." in prompt
    assert "erfinde nichts" in prompt.lower()


def test_same_module_code_in_multiple_handbooks_requires_clarification():
    results = []
    for rank, source in enumerate(("cl_bsc.pdf", "inf_bsc.pdf"), start=1):
        chunk = Chunk(
            chunk_id=f"{source}:P1",
            doc_id=source,
            title=source,
            source_path=source,
            text="P1",
            module_code="P1",
            section="Zugeordnete Modulteile",
        )
        results.append(SearchResult(chunk, 1.0, rank))

    assert clarification_needed("Wie viele ECTS hat P1?", results)


def test_ects_fact_is_extracted_deterministically():
    chunk = Chunk(
        chunk_id="wp3:ects",
        doc_id="cl_bsc.pdf",
        title="cl_bsc.pdf",
        source_path="cl_bsc.pdf",
        text="Im Modul müssen insgesamt 9 ECTS-Punkte erworben werden.",
        module_code="WP3",
        module_title="Information Retrieval",
        section="Zugeordnete Modulteile",
    )
    answer = structured_field_answer(
        "Wie viele ECTS hat WP3 Information Retrieval?",
        [SearchResult(chunk, 1.0, 1)],
    )

    assert answer == "WP3 Information Retrieval umfasst 9 ECTS-Punkte. (Quelle 1)"
