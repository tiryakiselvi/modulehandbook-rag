from __future__ import annotations

from pathlib import Path
from typing import Any
import html

import streamlit as st

from modulehandbook_rag.bm25_retrieval import BM25Retriever
from modulehandbook_rag.dense_retrieval import DenseRetriever
from modulehandbook_rag.handbook_catalog import (
    HANDBOOKS,
    infer_handbook_keys,
    match_chunk_to_filenames,
    recommended_keys,
    selected_filenames,
)
from modulehandbook_rag.hybrid_retrieval import HybridRetriever
from modulehandbook_rag.query_understanding import analyse_query, recommended_retriever
from modulehandbook_rag.rag import answer_from_results, llm_answer_from_results
from modulehandbook_rag.utils import read_jsonl

try:
    from modulehandbook_rag.llm import LLMError, OllamaClient
except Exception:  # pragma: no cover
    LLMError = RuntimeError
    OllamaClient = None


st.set_page_config(
    page_title="Modulhandbuch-RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --paper: #fbfcff;
  --ink: #07142f;
  --muted: #66718a;
  --line: rgba(22, 31, 63, 0.12);
  --card: rgba(255, 255, 255, 0.84);
  --accent: #5f7cff;
  --accent-2: #9b74ff;
  --accent-3: #67d7ff;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 10% 10%, rgba(95, 124, 255, 0.14), transparent 25%),
    radial-gradient(circle at 85% 8%, rgba(103, 215, 255, 0.16), transparent 27%),
    radial-gradient(circle at 90% 82%, rgba(155, 116, 255, 0.16), transparent 30%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 48%, #f8f6ff 100%);
  color: var(--ink);
}
[data-testid="stSidebar"] {
  background: rgba(255, 255, 255, 0.74);
  border-right: 1px solid var(--line);
  backdrop-filter: blur(18px);
}
.block-container {
  padding-top: 2rem;
  max-width: 1240px;
}
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  letter-spacing: -0.045em;
  color: var(--ink);
}
.hero {
  padding: 2.1rem 2.3rem;
  border: 1px solid var(--line);
  border-radius: 34px;
  background: rgba(255,255,255,0.77);
  backdrop-filter: blur(18px);
  box-shadow: 0 28px 80px rgba(25, 37, 80, 0.11);
  position: relative;
  overflow: hidden;
}
.hero:after {
  content: "";
  position: absolute;
  width: 250px;
  height: 250px;
  border-radius: 999px;
  right: -70px;
  top: -82px;
  background: linear-gradient(135deg, rgba(95,124,255,.20), rgba(155,116,255,.16), rgba(103,215,255,.14));
}
.eyebrow {
  display: inline-flex;
  gap: .45rem;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: .42rem .78rem;
  background: rgba(255,255,255,.82);
  color: var(--muted);
  font-size: .84rem;
  font-weight: 700;
  margin-bottom: 1rem;
}
.hero h1 {
  font-size: clamp(2.4rem, 5.2vw, 5.2rem);
  line-height: .92;
  margin: 0 0 .9rem 0;
}
.hero p {
  color: var(--muted);
  max-width: 780px;
  font-size: 1.08rem;
  line-height: 1.56;
}
.chip-row { display: flex; flex-wrap: wrap; gap: .58rem; margin-top: 1.22rem; }
.chip {
  border-radius: 999px;
  background: rgba(95,124,255,.10);
  border: 1px solid rgba(95,124,255,.18);
  color: #3349af;
  padding: .52rem .78rem;
  font-weight: 740;
  font-size: .88rem;
}
.result-card, .answer-card, .empty-card, .analysis-card {
  border: 1px solid var(--line);
  border-radius: 28px;
  padding: 1.1rem 1.2rem;
  background: rgba(255,255,255,0.82);
  box-shadow: 0 18px 55px rgba(31, 42, 86, 0.07);
}
.answer-card { border-left: 7px solid var(--accent); }
.result-card { margin-bottom: .95rem; }
.analysis-card { margin: .8rem 0 1rem 0; }
.rank-pill, .analysis-pill {
  display: inline-flex;
  border-radius: 999px;
  padding: .28rem .64rem;
  background: rgba(95,124,255,.12);
  color: #3349af;
  font-weight: 800;
  font-size: .79rem;
  margin: .15rem .3rem .15rem 0;
}
.source-line { color: var(--muted); font-size: .86rem; margin-top: .25rem; }
.tiny-note { color: var(--muted); font-size: .84rem; }
.stButton>button {
  border-radius: 999px !important;
  min-height: 3.35rem !important;
  padding: .78rem 1.12rem !important;
  border: 0 !important;
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  color: white !important;
  font-weight: 850 !important;
  box-shadow: 0 14px 30px rgba(95, 124, 255, .25) !important;
}
/* Abgerundetes Texteingabefeld. Mehrere Selektoren decken aktuelle Streamlit-Versionen ab. */
[data-testid="stTextInput"] input,
.stTextInput input,
input[aria-label="Frage"] {
  border-radius: 999px !important;
  min-height: 3.35rem !important;
  padding: 0.85rem 1.2rem !important;
  border: 1px solid rgba(95,124,255,.24) !important;
  background: rgba(255,255,255,.90) !important;
  box-shadow: 0 12px 32px rgba(31, 42, 86, 0.07) !important;
}
[data-testid="stTextInput"] input:focus,
.stTextInput input:focus {
  border-color: rgba(95,124,255,.72) !important;
  box-shadow: 0 0 0 4px rgba(95,124,255,.12), 0 14px 36px rgba(31,42,86,.08) !important;
}
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
  border-radius: 999px !important;
}
[data-testid="stMetric"] {
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: .8rem 1rem;
  background: rgba(255,255,255,.72);
}
[data-testid="stMetricValue"] { letter-spacing: -0.04em; }
hr { border: none; height: 1px; background: var(--line); margin: 1.15rem 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

EXAMPLE_QUESTIONS = {
    "Deutsch": [
        "Welche Veranstaltung behandelt Information Retrieval?",
        "Welche Module behandeln Suchmaschinen?",
        "Welche Prüfungsform hat WP3 Information Retrieval?",
        "Welche Inhalte hat der Master Computerlinguistik?",
    ],
    "English": [
        "Which course covers information retrieval?",
        "What is the exam type for Information Retrieval?",
        "Which modules are about search engines?",
        "Which modules are in the Computer Linguistics master program?",
    ],
    "Türkçe": [
        "Bilgi erişimi ile ilgili hangi ders var?",
        "Information Retrieval dersinin sınav şekli nedir?",
        "Arama motorlarını hangi modül ele alıyor?",
        "Bilgisayar dilbilimi yüksek lisansında hangi modüller var?",
    ],
}

LANGUAGE_NOTES = {
    "Auto": "Die Fragesprache wird automatisch als Deutsch, English oder Türkçe erkannt.",
    "Deutsch": "Deutsch: Auto wählt je nach Anfrage BM25 oder Hybrid.",
    "English": "English: Hybrid oder Dense gleicht die englische Frage mit deutschen Handbuchtexten ab.",
    "Türkçe": "Türkçe: Hybrid oder Dense gleicht die türkische Frage mit deutschen Handbuchtexten ab.",
}


def segmented(label: str, options: list[str], default: str) -> str:
    if hasattr(st, "segmented_control"):
        value = st.segmented_control(label, options, default=default)  # type: ignore[attr-defined]
        return value or default
    index = options.index(default) if default in options else 0
    return st.radio(label, options, index=index, horizontal=True)


@st.cache_data(show_spinner=False)
def load_chunks(chunks_path: str) -> list[Any]:
    path = Path(chunks_path)
    if not path.exists():
        return []
    return read_jsonl(path)


@st.cache_resource(show_spinner=False)
def build_retriever(
    kind: str,
    chunks_key: str,
    _chunks: tuple[Any, ...],
    section_boost: float,
    query_expansion: bool,
    alpha: float,
):
    chunk_list = list(_chunks)
    if kind == "BM25":
        return BM25Retriever(chunk_list, section_boost=section_boost, use_query_expansion=query_expansion)
    if kind == "Dense":
        return DenseRetriever(chunk_list)
    if kind == "Hybrid":
        return HybridRetriever(
            chunk_list,
            alpha=alpha,
            section_boost=section_boost,
            use_query_expansion=query_expansion,
        )
    raise ValueError(kind)


def chunk_attr(chunk: Any, name: str, default: str = "") -> str:
    if isinstance(chunk, dict):
        value = chunk.get(name, default)
    else:
        value = getattr(chunk, name, default)
    return "" if value is None else str(value)


def result_text(result: Any) -> str:
    return chunk_attr(result.chunk, "text")


def result_title(result: Any) -> str:
    chunk = result.chunk
    parts = [
        chunk_attr(chunk, "module_code"),
        chunk_attr(chunk, "module_title"),
        chunk_attr(chunk, "section"),
    ]
    parts = [part for part in parts if part]
    return " · ".join(parts) if parts else "Gefundene Evidenz"


def result_source(result: Any) -> str:
    chunk = result.chunk
    for field in ("source", "source_path", "doc_id", "document", "filename"):
        value = chunk_attr(chunk, field)
        if value:
            return value
    return "Quelle nicht in Metadaten verfügbar"


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">🎓 LMU Modulhandbuch-RAG</div>
          <h1>Suche in Modulhandbüchern.</h1>
          <p>
            Die Anwendung durchsucht ausgewählte Modulhandbücher und zeigt die relevantesten
            Evidenzstellen mit Quelle, Abschnitt und Score. Je nach Anfrage können lexikalische
            und semantische Suche kombiniert werden.
          </p>
          <div class="chip-row">
            <span class="chip">Korpusauswahl</span>
            <span class="chip">BM25 · Dense · Hybrid</span>
            <span class="chip">Deutsch · English · Türkçe</span>
            <span class="chip">sichtbare Evidenz</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result: Any) -> None:
    safe_text = html.escape(result_text(result)[:1800]).replace("\n", "<br />")
    safe_title = html.escape(result_title(result))
    safe_source = html.escape(result_source(result))
    st.markdown(
        f"""
        <div class="result-card">
          <div><span class="rank-pill">#{result.rank}</span><b>{safe_title}</b></div>
          <div class="source-line">Score {result.score:.3f} · {safe_source}</div>
          <hr />
          <div>{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fixed_selection(corpus_mode: str) -> list[str]:
    if corpus_mode == "Recommended demo corpus":
        return recommended_keys()
    if corpus_mode == "Alle verfügbaren Modulhandbücher":
        return [h.key for h in HANDBOOKS]
    return []


render_hero()
st.write("")

with st.sidebar:
    st.markdown("### Korpus")
    corpus_mode = st.radio(
        "Welche Modulhandbücher sollen durchsucht werden?",
        [
            "Automatisch aus der Frage",
            "Recommended demo corpus",
            "Ein spezifisches Modulhandbuch",
            "Alle verfügbaren Modulhandbücher",
            "Eigene Auswahl",
        ],
        index=0,
    )

    manual_keys: list[str] = []
    if corpus_mode == "Ein spezifisches Modulhandbuch":
        label_to_key = {h.label: h.key for h in HANDBOOKS}
        chosen_label = st.selectbox("Modulhandbuch", list(label_to_key.keys()), index=0)
        manual_keys = [label_to_key[chosen_label]]
    elif corpus_mode == "Eigene Auswahl":
        defaults = recommended_keys()
        label_to_key = {h.label: h.key for h in HANDBOOKS}
        default_labels = [h.label for h in HANDBOOKS if h.key in defaults]
        chosen_labels = st.multiselect("Modulhandbücher", list(label_to_key.keys()), default=default_labels)
        manual_keys = [label_to_key[label] for label in chosen_labels]

    st.markdown("### Sprache")
    language_hint = segmented("Sprache der Frage", ["Auto", "Deutsch", "English", "Türkçe"], "Auto")
    st.caption(LANGUAGE_NOTES[language_hint])

    st.markdown("### Retrieval")
    chunk_file = st.selectbox(
        "Chunk-Datei",
        [
            "data/processed/chunks_field.jsonl",
            "data/processed/chunks_module.jsonl",
            "data/processed/chunks_naive.jsonl",
            "data/processed/chunks.jsonl",
        ],
        index=0,
    )
    retriever_choice = segmented("Retriever", ["Auto", "BM25", "Dense", "Hybrid"], "Auto")
    top_k = st.slider("Evidence chunks", 1, 8, 3)
    section_boost = st.slider("Section Boost", 0.0, 12.0, 8.0, 0.5)
    query_expansion = st.toggle("Query Expansion", value=True)
    alpha = st.slider("Hybrid Dense-Gewicht", 0.0, 1.0, 0.25, 0.05)

    st.markdown("### Antwort")
    answer_mode = st.radio("Antwortmodus", ["Evidence summary", "Ollama LLM answer"], index=0)
    model = st.text_input("Ollama-Modell", value="llama3.2:3b")

chunks = load_chunks(chunk_file)

if not chunks:
    st.markdown(
        """
        <div class="empty-card">
          <b>Noch keine Chunks gefunden.</b><br />
          Erzeuge sie zuerst, zum Beispiel:<br /><br />
          <code>python -m modulehandbook_rag.cli ingest data/raw --chunking field --out data/processed/chunks_field.jsonl</code>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.write("")
query_col, example_col = st.columns([0.75, 0.25])
with query_col:
    query = st.text_input(
        "Frage",
        placeholder="Stelle eine Frage zum Modulhandbuch …",
        label_visibility="collapsed",
        key="main_query",
    )
with example_col:
    example_language = language_hint if language_hint in EXAMPLE_QUESTIONS else "Deutsch"
    examples = EXAMPLE_QUESTIONS[example_language]
    example = st.selectbox("Beispiele", ["Beispiel wählen …"] + examples)
    if example != "Beispiel wählen …" and not query:
        query = example

run = st.button("Modulhandbücher durchsuchen", use_container_width=True)

# Before the first search, show the default scope without pretending it was inferred.
preview_keys = manual_keys or fixed_selection(corpus_mode) or recommended_keys()
preview_filenames = selected_filenames(preview_keys)
preview_chunks = [chunk for chunk in chunks if match_chunk_to_filenames(chunk, preview_filenames)]

metric1, metric2, metric3 = st.columns(3)
with metric1:
    st.metric("Geladene Chunks", len(chunks))
with metric2:
    st.metric("Aktueller Vorschau-Korpus", len(preview_chunks))
with metric3:
    st.metric("Modulhandbücher", len(preview_keys))

if run and query.strip():
    analysis = analyse_query(query.strip(), language_hint)

    if corpus_mode == "Automatisch aus der Frage":
        chosen_keys = infer_handbook_keys(analysis)
    elif manual_keys:
        chosen_keys = manual_keys
    else:
        chosen_keys = fixed_selection(corpus_mode)

    filenames = selected_filenames(chosen_keys)
    filtered_chunks = [chunk for chunk in chunks if match_chunk_to_filenames(chunk, filenames)]

    if not filtered_chunks:
        st.error(
            "Keine Chunks passen zur Korpus-Auswahl. Erzeuge die Chunks aus allen PDFs neu oder wähle vorübergehend alle Modulhandbücher."
        )
        st.stop()

    actual_retriever = recommended_retriever(analysis) if retriever_choice == "Auto" else retriever_choice

    handbook_labels = [h.label for h in HANDBOOKS if h.key in chosen_keys]
    analysis_pills = [
        f"Sprache: {analysis.language}",
        f"Retriever: {actual_retriever}",
        f"Korpus: {len(chosen_keys)} Handbuch/Handbücher",
        *analysis.explanation,
    ]
    pills_html = "".join(f'<span class="analysis-pill">{html.escape(pill)}</span>' for pill in analysis_pills)
    st.markdown(
        f"""
        <div class="analysis-card">
          <b>So interpretiert die Suche deine Frage</b><br /><br />
          {pills_html}
          <div class="source-line">Ausgewählt: {html.escape(' · '.join(handbook_labels))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        retriever = build_retriever(
            actual_retriever,
            f"{chunk_file}:{','.join(chosen_keys)}:{len(filtered_chunks)}",
            tuple(filtered_chunks),
            section_boost,
            query_expansion,
            alpha,
        )
        with st.spinner("Evidenz wird gesucht …"):
            if actual_retriever == "BM25":
                results = retriever.search(analysis.bm25_query, top_k=top_k)
            elif actual_retriever == "Hybrid":
                results = retriever.search(query, top_k=top_k, bm25_query=analysis.bm25_query)
            else:
                results = retriever.search(query, top_k=top_k)
    except Exception as exc:
        if actual_retriever in {"Dense", "Hybrid"}:
            st.warning(
                "Dense/Hybrid ist nicht verfügbar. Die App fällt auf BM25 zurück. Installiere für den vollen Modus: pip install -e \".[dense]\""
            )
            fallback = BM25Retriever(filtered_chunks, section_boost=section_boost, use_query_expansion=query_expansion)
            results = fallback.search(analysis.bm25_query, top_k=top_k)
            actual_retriever = "BM25 Fallback"
        else:
            raise exc

    st.markdown("## Antwort")
    if answer_mode == "Ollama LLM answer":
        if OllamaClient is None:
            st.error("Ollama-Support ist in dieser Umgebung nicht verfügbar.")
        else:
            client = OllamaClient(model=model)
            language_instruction = (
                f"Antworte in {analysis.language}. Nutze nur die gefundene Evidenz. "
                "Deutsche Modultitel und Feldbezeichnungen dürfen unverändert bleiben."
            )
            try:
                answer = llm_answer_from_results(
                    query,
                    results,
                    lambda prompt: client.generate(f"{language_instruction}\n\n{prompt}", temperature=0.0),
                )
            except LLMError as exc:
                answer = f"Ollama-Fehler: {exc}"
            safe_answer = html.escape(str(answer)).replace('\n', '<br />')
            st.markdown(f"<div class='answer-card'>{safe_answer}</div>", unsafe_allow_html=True)
    else:
        answer = answer_from_results(query, results)
        safe_answer = html.escape(str(answer)).replace('\n', '<br />')
        st.markdown(f"<div class='answer-card'>{safe_answer}</div>", unsafe_allow_html=True)

    st.markdown("## Gefundene Evidenz")
    for result in results:
        render_result(result)

    with st.expander("Ausgewählte Modulhandbücher", expanded=False):
        for handbook in HANDBOOKS:
            if handbook.key in chosen_keys:
                st.markdown(
                    f"**{handbook.label}**  \n{handbook.variant}  \n`{handbook.filename}`  \n<span class='tiny-note'>{handbook.note}</span>",
                    unsafe_allow_html=True,
                )
elif run:
    st.info("Gib zuerst eine Frage ein.")
else:
    st.caption(
        "Beispiel: Welche Veranstaltung behandelt Information Retrieval?"
    )
