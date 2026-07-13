from modulehandbook_rag.bm25_retrieval import chunk_index_text
from modulehandbook_rag.schemas import Chunk


def test_embedding_text_contains_document_module_and_field_context():
    chunk = Chunk(
        chunk_id="wp3:field:prerequisite:part:0",
        doc_id="cl-bsc",
        title="Computerlinguistik Bachelor",
        source_path="cl-bsc.pdf",
        text="Teilnahmevoraussetzung keine",
        module_code="WP3",
        module_title="Information Retrieval",
        section="Teilnahmevoraussetzung",
    )

    text = chunk_index_text(chunk)
    assert "Dokument: Computerlinguistik Bachelor" in text
    assert "Modul: WP3 Information Retrieval" in text
    assert "Feld: Teilnahmevoraussetzung" in text
    assert "Inhalt: Teilnahmevoraussetzung keine" in text
