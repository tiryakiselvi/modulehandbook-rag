from modulehandbook_rag.handbook_catalog import infer_handbook_keys
from modulehandbook_rag.query_understanding import analyse_query, recommended_retriever


def test_topic_query_without_module_code_uses_hybrid():
    analysis = analyse_query("Welche Veranstaltung behandelt Information Retrieval?")
    assert not analysis.has_module_code
    assert recommended_retriever(analysis) == "Hybrid"
    assert "Information Retrieval" in analysis.bm25_query


def test_turkish_query_is_expanded_for_german_bm25():
    analysis = analyse_query("Bilgi erişimi ile ilgili hangi ders var?")
    assert analysis.language == "Türkçe"
    assert "Suchmaschinen" in analysis.bm25_query
    assert recommended_retriever(analysis) == "Hybrid"


def test_automatic_corpus_routing():
    cl_master = analyse_query("Welche Inhalte hat der Master Computerlinguistik?")
    assert infer_handbook_keys(cl_master) == ["cl_msc"]

    inf_sose = analyse_query("Welche Module gibt es im Informatik Master bei Beginn im SoSe?")
    assert infer_handbook_keys(inf_sose) == ["inf_msc_sose"]

    inf_minor = analyse_query("Welche Module gehören zum Informatik Bachelor Nebenfach 60 ECTS?")
    assert infer_handbook_keys(inf_minor) == ["inf_bsc_minor_60"]
