from modulehandbook_rag.evaluation import EvalQuery


def test_eval_query_reads_id_type_and_documents():
    query = EvalQuery.from_dict(
        {
            "id": "q01",
            "query": "Wie viele ECTS hat WP3?",
            "query_type": "numerical",
            "relevant_documents": ["data/raw/cl_bsc_modulhandbuch.pdf"],
            "relevant_modules": ["WP3"],
            "relevant_sections": ["Zugeordnete Modulteile"],
        }
    )
    assert query.query_id == "q01"
    assert query.query_type == "numerical"
    assert query.relevant_documents == {"cl_bsc_modulhandbuch.pdf"}
    assert query.relevant_modules == {"WP3"}
    assert query.relevant_sections == {"Zugeordnete Modulteile"}
