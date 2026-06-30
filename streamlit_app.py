from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modulehandbook_rag.bm25_retrieval import BM25Retriever
from modulehandbook_rag.dense_retrieval import DenseRetriever
from modulehandbook_rag.hybrid_retrieval import HybridRetriever
from modulehandbook_rag.rag import answer_from_results
from modulehandbook_rag.utils import read_jsonl


st.set_page_config(page_title="LMU Modulhandbuch Suche", layout="wide")

CORPORA = {
    "Bachelor Computerlinguistik": PROJECT_DIR / "data/processed/cl_bachelor_current_field.jsonl",
    "Master Computerlinguistik": PROJECT_DIR / "data/processed/cl_master_current_field.jsonl",
    "Master Informatik": PROJECT_DIR / "data/processed/informatik_master_current_field.jsonl",
}


@st.cache_data(show_spinner=False)
def load_chunks(path: str):
    return read_jsonl(Path(path))


@st.cache_resource(show_spinner=True)
def make_retriever(name: str, path: str, alpha: float, section_boost: float):
    chunks = load_chunks(path)
    if name == "BM25":
        return BM25Retriever(chunks, section_boost=section_boost)
    if name == "Hybrid":
        return HybridRetriever(chunks, alpha=alpha, section_boost=section_boost)
    return DenseRetriever(chunks)


def source_line(result) -> str:
    chunk = result.chunk
    parts = []
    if chunk.module_code:
        parts.append(chunk.module_code)
    if chunk.module_title:
        parts.append(chunk.module_title)
    if chunk.section:
        parts.append(chunk.section)
    if chunk.page_number:
        parts.append(f"Seite {chunk.page_number}")
    return " | ".join(parts) or chunk.title


st.title("LMU Modulhandbuch Suche")
st.caption("Strukturierte Suche über vorbereitete Modulhandbuch- und Ordnungstexte.")

with st.sidebar:
    st.header("Einstellungen")
    corpus_name = st.selectbox("Korpus", list(CORPORA))
    retriever_name = st.selectbox("Retrieval", ["BM25", "Hybrid", "Dense"], index=1)
    top_k = st.slider("Trefferanzahl", min_value=1, max_value=8, value=3)
    alpha = st.slider("Hybrid-Gewichtung", 0.0, 1.0, 0.5, 0.05)
    section_boost = st.slider("Abschnittsgewichtung", 0.0, 10.0, 0.0, 0.5)

query = st.text_input(
    "Frage",
    value="Wie viele ECTS hat WP3 Information Retrieval?",
)

chunks_path = CORPORA[corpus_name]
if not chunks_path.exists():
    st.error(f"Chunk-Datei nicht gefunden: {chunks_path}")
    st.stop()

if st.button("Suchen", type="primary"):
    retriever = make_retriever(retriever_name, str(chunks_path), alpha, section_boost)
    results = retriever.search(query, top_k=top_k)

    answer_col, hits_col = st.columns([1, 1.35])
    with answer_col:
        st.subheader("Antwort aus Quellen")
        st.text(answer_from_results(query, results))

    with hits_col:
        st.subheader("Gefundene Quellen")
        for result in results:
            with st.expander(
                f"#{result.rank} | Score {result.score:.3f} | {source_line(result)}",
                expanded=result.rank == 1,
            ):
                st.write(result.chunk.text[:1800])
                st.caption(f"Datei: {result.chunk.source_path}")
else:
    st.write("Korpus und Retrieval auswählen, Frage eingeben und Suche starten.")
