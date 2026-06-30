from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .bm25_retrieval import BM25Retriever
from .chunking import make_chunks
from .citations import format_result
from .data_loader import load_documents
from .dense_retrieval import DenseRetriever
from .evaluation import evaluate_by_query_type, evaluate_results, load_eval_queries
from .hybrid_retrieval import HybridRetriever
from .llm import LLMError, OllamaClient
from .rag import answer_from_results, llm_answer_from_results
from .utils import read_jsonl, write_jsonl

app = typer.Typer(help="RAG-style search over university module handbooks.")
console = Console()


@app.command()
def ingest(
    input_path: Path = typer.Argument(..., help="PDF/TXT/MD file or directory."),
    out: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Output JSONL path."),
    chunking: Literal["naive", "module", "field"] = typer.Option("module", help="Chunking strategy."),
    chunk_size: int = typer.Option(900, help="Size for naive chunking."),
    overlap: int = typer.Option(120, help="Overlap for naive chunking."),
) -> None:
    docs = load_documents(input_path)
    chunks = make_chunks(docs, mode=chunking, chunk_size=chunk_size, overlap=overlap)
    write_jsonl(chunks, out)
    console.print(f"Loaded {len(docs)} document/page units.")
    console.print(f"Wrote {len(chunks)} chunks to [bold]{out}[/bold].")


@app.command()
def stats(
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
) -> None:
    chunk_list = read_jsonl(chunks)
    modules = sorted({c.module_code for c in chunk_list if c.module_code})
    sections = sorted({c.section for c in chunk_list if c.section})
    document_types = sorted({c.document_type for c in chunk_list if c.document_type})
    console.print(f"Chunks: {len(chunk_list)}")
    console.print(f"Detected modules: {len(modules)}")
    if modules:
        console.print(", ".join(modules))
    console.print(f"Sections: {len(sections)}")
    if sections:
        console.print(", ".join(sections[:30]))
    console.print("Document types: " + (", ".join(document_types) if document_types else "none"))


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of results."),
    section_boost: float = typer.Option(0.0, help="Optional BM25 field boost; 0 is the clean baseline."),
    dense_model: str = typer.Option("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", help="Sentence-Transformers model."),
    alpha: float = typer.Option(0.5, min=0.0, max=1.0, help="Dense weight for hybrid retrieval."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, dense_model, alpha)
    results = retr.search(query, top_k=top_k)
    for result in results:
        console.print(Panel(format_result(result), title=f"Treffer {result.rank}"))


@app.command()
def ask(
    query: str = typer.Argument(..., help="Question."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of context chunks."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list)
    results = retr.search(query, top_k=top_k)
    answer = answer_from_results(query, results)
    console.print(Panel(answer, title="Antwort"))


@app.command("ask-llm")
def ask_llm(
    query: str = typer.Argument(..., help="Question."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(3, help="Number of context chunks."),
    model: str = typer.Option("llama3.1:8b", help="Ollama model name."),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL."),
    temperature: float = typer.Option(0.0, help="LLM temperature."),
) -> None:
    """Ask a question and generate a grounded LLM answer with Ollama."""
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list)
    results = retr.search(query, top_k=top_k)
    client = OllamaClient(model=model, base_url=ollama_url)
    try:
        answer = llm_answer_from_results(
            query,
            results,
            lambda prompt: client.generate(prompt, temperature=temperature),
        )
    except LLMError as exc:
        console.print(Panel(str(exc), title="LLM-Fehler", style="red"))
        raise typer.Exit(code=1) from exc
    console.print(Panel(answer, title=f"LLM-RAG Antwort ({model})"))


@app.command("evaluate")
def evaluate_command(
    eval_file: Path = typer.Option(Path("data/eval/demo_queries.jsonl"), help="JSONL/CSV file with evaluation queries."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: Literal["bm25", "dense", "hybrid"] = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Evaluation cutoff."),
    require_section: bool = typer.Option(False, help="Require both correct module and correct field/section."),
    section_boost: float = typer.Option(0.0, help="Optional BM25 field boost; report it as an ablation."),
    dense_model: str = typer.Option("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", help="Sentence-Transformers model."),
    alpha: float = typer.Option(0.5, min=0.0, max=1.0, help="Dense weight for hybrid retrieval."),
) -> None:
    eval_queries = load_eval_queries(eval_file)
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, dense_model, alpha)
    grouped_metrics = evaluate_by_query_type(eval_queries, retr.search, chunk_list, k=top_k, require_section=require_section)

    table = Table(title=f"Evaluation: {retriever} on {chunks}")
    table.add_column("Group")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for group, metrics in grouped_metrics.items():
        for key, value in metrics.items():
            table.add_row(group, key, str(int(value)) if key == "queries" else f"{value:.3f}")
    console.print(table)


def _make_retriever(name: str, chunks, section_boost: float = 0.0, dense_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", alpha: float = 0.5):
    if name == "bm25":
        return BM25Retriever(chunks, section_boost=section_boost)
    if name == "dense":
        return DenseRetriever(chunks, model_name=dense_model)
    if name == "hybrid":
        return HybridRetriever(chunks, alpha=alpha, section_boost=section_boost, model_name=dense_model)
    raise ValueError(f"Unknown retriever: {name}")


if __name__ == "__main__":
    app()
