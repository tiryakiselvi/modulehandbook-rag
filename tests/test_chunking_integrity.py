from modulehandbook_rag.chunking import field_chunks, module_chunks
from modulehandbook_rag.schemas import Document


def test_repeated_sections_keep_all_parts_with_unique_ids():
    text = (
        "Modul: WP3 Information Retrieval\n"
        "Englischer Modultitel Information Retrieval\n"
        "Inhalte\n" + "Erster Abschnitt. " * 20 + "\n"
        "Inhalte\n" + "Zweiter Abschnitt. " * 20
    )
    chunks = field_chunks(
        [Document("doc", "Handbuch", "handbook.pdf", text, 1)]
    )

    content_chunks = [chunk for chunk in chunks if chunk.section == "Inhalte"]
    assert len(content_chunks) == 2
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
    assert content_chunks[0].chunk_id.endswith(":part:0")
    assert content_chunks[1].chunk_id.endswith(":part:1")


def test_repeated_module_codes_keep_unique_module_ids():
    first = "Modul: P1 Erstes Modul\n" + "Inhalte A. " * 30
    second = "Modul: P1 Zweites Modul\n" + "Inhalte B. " * 30
    chunks = module_chunks(
        [Document("doc", "Handbuch", "handbook.pdf", first + "\n" + second, 1)]
    )

    assert len(chunks) == 2
    assert len({chunk.chunk_id for chunk in chunks}) == 2
    assert chunks[0].chunk_id.endswith(":part:0")
    assert chunks[1].chunk_id.endswith(":part:1")
