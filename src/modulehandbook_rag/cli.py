from __future__ import annotations

import csv
import json
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
from .evaluation import evaluate_by_query_type, evaluate_per_query, evaluate_results, load_eval_queries
from .handbook_config import load_handbook_config
from .hybrid_retrieval import HybridRetriever
from .llm import LLMError, OllamaClient
from .rag import answer_from_results, llm_answer_from_results
from .utils import ensure_parent, read_jsonl, write_jsonl

app = typer.Typer(help="RAG-style search over university module handbooks.")
console = Console()

RetrieverName = Literal["bm25", "dense", "hybrid"]


@app.command()
def ingest(
    input_path: Path = typer.Argument(..., help="PDF/TXT/MD file or directory."),
    out: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Output JSONL path."),
    chunking: Literal["naive", "module", "field"] = typer.Option("module", help="Chunking strategy."),
    chunk_size: int = typer.Option(900, help="Size for naive chunking."),
    overlap: int = typer.Option(120, help="Overlap for naive chunking."),
    config: Path | None = typer.Option(None, help="Optional handbook layout config JSON."),
) -> None:
    handbook_config = load_handbook_config(config)
    docs = load_documents(input_path)
    chunks = make_chunks(
        docs,
        mode=chunking,
        chunk_size=chunk_size,
        overlap=overlap,
        module_pattern=handbook_config.module_pattern,
        section_labels=handbook_config.section_labels,
    )
    write_jsonl(chunks, out)
    console.print(f"Loaded {len(docs)} document/page units.")
    console.print(f"Wrote {len(chunks)} chunks to [bold]{out}[/bold].")
    if config:
        console.print(f"Used config: [bold]{config}[/bold] ({handbook_config.name})")


@app.command()
def stats(
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
) -> None:
    chunk_list = read_jsonl(chunks)
    modules = sorted({c.module_code for c in chunk_list if c.module_code})
    sections = sorted({c.section for c in chunk_list if c.section})
    console.print(f"Chunks: {len(chunk_list)}")
    console.print(f"Detected modules: {len(modules)}")
    if modules:
        console.print(", ".join(modules))
    console.print(f"Sections: {len(sections)}")
    if sections:
        console.print(", ".join(sections[:40]))


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: RetrieverName = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of results."),
    section_boost: float = typer.Option(8.0, help="BM25 section boost. Use 0 for the BM25 ablation baseline."),
    query_expansion: bool = typer.Option(True, "--query-expansion/--no-query-expansion", help="Use domain-specific BM25 query expansion."),
    alpha: float = typer.Option(0.5, help="Hybrid weight for dense retrieval. 0=BM25 only, 1=dense only."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, query_expansion, alpha)
    results = retr.search(query, top_k=top_k)
    for result in results:
        console.print(Panel(format_result(result), title=f"Treffer {result.rank}"))


@app.command()
def ask(
    query: str = typer.Argument(..., help="Question."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: RetrieverName = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Number of context chunks."),
    section_boost: float = typer.Option(8.0, help="BM25 section boost. Use 0 for the BM25 ablation baseline."),
    query_expansion: bool = typer.Option(True, "--query-expansion/--no-query-expansion", help="Use domain-specific BM25 query expansion."),
    alpha: float = typer.Option(0.5, help="Hybrid weight for dense retrieval. 0=BM25 only, 1=dense only."),
) -> None:
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, query_expansion, alpha)
    results = retr.search(query, top_k=top_k)
    answer = answer_from_results(query, results)
    console.print(Panel(answer, title="Antwort"))


@app.command("ask-llm")
def ask_llm(
    query: str = typer.Argument(..., help="Question."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: RetrieverName = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(3, help="Number of context chunks."),
    model: str = typer.Option("llama3.1:8b", help="Ollama model name."),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL."),
    temperature: float = typer.Option(0.0, help="LLM temperature."),
    seed: int = typer.Option(42, help="Generation seed used for reproducibility checks."),
    section_boost: float = typer.Option(8.0, help="BM25 section boost. Use 0 for the BM25 ablation baseline."),
    query_expansion: bool = typer.Option(True, "--query-expansion/--no-query-expansion", help="Use domain-specific BM25 query expansion."),
    alpha: float = typer.Option(0.5, help="Hybrid weight for dense retrieval. 0=BM25 only, 1=dense only."),
) -> None:
    """Ask a question and generate a grounded LLM answer with Ollama."""

    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, query_expansion, alpha)
    results = retr.search(query, top_k=top_k)
    client = OllamaClient(model=model, base_url=ollama_url)

    try:
        answer = llm_answer_from_results(
            query,
            results,
            lambda prompt: client.generate(prompt, temperature=temperature, seed=seed),
        )
    except LLMError as exc:
        console.print(Panel(str(exc), title="LLM-Fehler", style="red"))
        raise typer.Exit(code=1) from exc

    console.print(Panel(answer, title=f"LLM-RAG Antwort ({model})"))


@app.command("evaluate")
def evaluate_command(
    eval_file: Path = typer.Option(Path("data/eval/retrieval_eval_queries.jsonl"), help="JSONL/CSV file with evaluation queries."),
    chunks: Path = typer.Option(Path("data/processed/chunks.jsonl"), help="Chunks JSONL path."),
    retriever: RetrieverName = typer.Option("bm25", help="Retriever type."),
    top_k: int = typer.Option(5, help="Evaluation cutoff."),
    require_section: bool = typer.Option(False, help="Require both correct module and correct field/section."),
    by_query_type: bool = typer.Option(False, help="Also report metrics grouped by query_type."),
    section_boost: float = typer.Option(8.0, help="BM25 section boost. Use 0 for the BM25 ablation baseline."),
    query_expansion: bool = typer.Option(True, "--query-expansion/--no-query-expansion", help="Use domain-specific BM25 query expansion."),
    alpha: float = typer.Option(0.5, help="Hybrid weight for dense retrieval. 0=BM25 only, 1=dense only."),
    out: Path | None = typer.Option(None, help="Optional JSON output file for metrics."),
    details_out: Path | None = typer.Option(None, help="Optional CSV with one auditable row per query."),
) -> None:
    eval_queries = load_eval_queries(eval_file)
    chunk_list = read_jsonl(chunks)
    retr = _make_retriever(retriever, chunk_list, section_boost, query_expansion, alpha)

    if by_query_type:
        grouped_metrics = evaluate_by_query_type(
            eval_queries,
            retr.search,
            chunk_list,
            k=top_k,
            require_section=require_section,
        )
    else:
        grouped_metrics = {
            "overall": evaluate_results(
                eval_queries,
                retr.search,
                chunk_list,
                k=top_k,
                require_section=require_section,
            )
        }

    _print_metrics_table(grouped_metrics, title=f"Evaluation: {retriever} on {chunks}")

    if out:
        ensure_parent(out)
        payload = {
            "eval_file": str(eval_file),
            "chunks": str(chunks),
            "retriever": retriever,
            "top_k": top_k,
            "require_section": require_section,
            "section_boost": section_boost,
            "query_expansion": query_expansion,
            "alpha": alpha,
            "metrics": grouped_metrics,
        }
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"Wrote metrics to [bold]{out}[/bold].")

    if details_out:
        ensure_parent(details_out)
        detail_rows = evaluate_per_query(
            eval_queries,
            retr.search,
            k=top_k,
            require_section=require_section,
        )
        with details_out.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(detail_rows[0].keys()))
            writer.writeheader()
            writer.writerows(detail_rows)
        console.print(f"Wrote per-query analysis to [bold]{details_out}[/bold].")


@app.command("benchmark")
def benchmark_command(
    eval_file: Path = typer.Option(Path("data/eval/retrieval_eval_queries.jsonl"), help="Evaluation query file."),
    chunks_dir: Path = typer.Option(Path("data/processed"), help="Directory containing chunks_naive/module/field.jsonl."),
    chunkings: str = typer.Option("naive,module,field", help="Comma-separated chunking names."),
    retrievers: str = typer.Option("bm25", help="Comma-separated retrievers: bm25,dense,hybrid."),
    top_k: int = typer.Option(3, help="Evaluation cutoff."),
    require_section: bool = typer.Option(False, help="Require both module and section match."),
    by_query_type: bool = typer.Option(False, help="Write one row per query_type in addition to overall."),
    section_boosts: str = typer.Option("8.0", help="Comma-separated BM25 section boosts, e.g. 0,8 for ablation."),
    query_expansion: bool = typer.Option(True, "--query-expansion/--no-query-expansion", help="Use domain-specific BM25 query expansion."),
    alpha: float = typer.Option(0.5, help="Hybrid weight for dense retrieval. 0=BM25 only, 1=dense only."),
    out_csv: Path = typer.Option(Path("outputs/evaluation_results.csv"), help="CSV output path."),
    out_md: Path = typer.Option(Path("docs/evaluation_results.md"), help="Markdown output path."),
) -> None:
    """Run comparison tables over chunking, retriever and ablation settings."""

    eval_queries = load_eval_queries(eval_file)
    rows: list[dict[str, str | float | int | bool]] = []
    chunking_names = [x.strip() for x in chunkings.split(",") if x.strip()]
    retriever_names = [x.strip() for x in retrievers.split(",") if x.strip()]
    section_boost_values = [float(x.strip()) for x in section_boosts.split(",") if x.strip()]

    for chunking_name in chunking_names:
        chunks_path = chunks_dir / f"chunks_{chunking_name}.jsonl"
        if not chunks_path.exists():
            console.print(f"[yellow]Skipping missing chunks file:[/yellow] {chunks_path}")
            continue

        chunk_list = read_jsonl(chunks_path)
        for retriever_name in retriever_names:
            for section_boost in section_boost_values:
                retr = _make_retriever(
                    retriever_name,
                    chunk_list,
                    section_boost=section_boost,
                    query_expansion=query_expansion,
                    alpha=alpha,
                )

                if by_query_type:
                    grouped_metrics = evaluate_by_query_type(
                        eval_queries,
                        retr.search,
                        chunk_list,
                        k=top_k,
                        require_section=require_section,
                    )
                else:
                    grouped_metrics = {
                        "overall": evaluate_results(
                            eval_queries,
                            retr.search,
                            chunk_list,
                            k=top_k,
                            require_section=require_section,
                        )
                    }

                for group_name, metrics in grouped_metrics.items():
                    rows.append(
                        {
                            "chunking": chunking_name,
                            "retriever": retriever_name,
                            "query_type": group_name,
                            "top_k": top_k,
                            "require_section": require_section,
                            "section_boost": section_boost,
                            "query_expansion": query_expansion,
                            "alpha": alpha if retriever_name == "hybrid" else "",
                            **metrics,
                        }
                    )

    if not rows:
        console.print("[red]No benchmark rows were produced.[/red]")
        raise typer.Exit(code=1)

    _write_benchmark_csv(rows, out_csv)
    _write_benchmark_md(rows, out_md, eval_file)
    _print_benchmark_table(rows)
    console.print(f"Wrote CSV to [bold]{out_csv}[/bold].")
    console.print(f"Wrote Markdown to [bold]{out_md}[/bold].")


def _make_retriever(
    name: str,
    chunks,
    section_boost: float = 8.0,
    query_expansion: bool = True,
    alpha: float = 0.5,
):
    if name == "bm25":
        return BM25Retriever(
            chunks,
            section_boost=section_boost,
            use_query_expansion=query_expansion,
        )
    if name == "dense":
        return DenseRetriever(chunks)
    if name == "hybrid":
        return HybridRetriever(
            chunks,
            alpha=alpha,
            section_boost=section_boost,
            use_query_expansion=query_expansion,
        )
    raise ValueError(f"Unknown retriever: {name}")


def _print_metrics_table(grouped_metrics: dict[str, dict[str, float]], title: str) -> None:
    first_metrics = next(iter(grouped_metrics.values()))
    table = Table(title=title)
    table.add_column("query_type")
    for key in first_metrics.keys():
        table.add_column(key, justify="right")

    for group, metrics in grouped_metrics.items():
        row = [group]
        for key, value in metrics.items():
            if key == "queries":
                row.append(str(int(value)))
            else:
                row.append(f"{value:.3f}")
        table.add_row(*row)
    console.print(table)


def _write_benchmark_csv(rows: list[dict[str, str | float | int | bool]], out_csv: Path) -> None:
    ensure_parent(out_csv)
    fieldnames = list(rows[0].keys())
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_benchmark_md(rows: list[dict[str, str | float | int | bool]], out_md: Path, eval_file: Path) -> None:
    ensure_parent(out_md)
    metric_keys = [
        key
        for key in rows[0].keys()
        if key
        not in {
            "chunking",
            "retriever",
            "query_type",
            "top_k",
            "require_section",
            "section_boost",
            "query_expansion",
            "alpha",
        }
    ]
    header = [
        "chunking",
        "retriever",
        "query_type",
        "top_k",
        "require_section",
        "section_boost",
        "query_expansion",
        "alpha",
        *metric_keys,
    ]

    lines = [
        "# Evaluation results",
        "",
        f"Evaluation file: `{eval_file}`",
        "",
        "The table is generated by `modulehandbook_rag.cli benchmark`. `section_boost = 0` is the BM25 ablation baseline; `section_boost = 8` is the domain-aware field boost used in the demo.",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]

    for row in rows:
        values = []
        for key in header:
            value = row[key]
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    lines.extend(
        [
            "",
            "## Reading the metrics",
            "",
            "- `hit@1`: whether the first ranked chunk is relevant.",
            "- `precision@k`: share of the top-k retrieved chunks that are relevant.",
            "- `recall@k`: share of all relevant chunks that were retrieved in the top-k.",
            "- `mrr`: mean reciprocal rank; higher means the first relevant result appears earlier.",
            "- `ndcg@k`: ranking quality with higher weight for relevant results near the top.",
            "",
            "## Recommended presentation reading",
            "",
            "Report relaxed module-level retrieval separately from strict field-level retrieval. For RAG answer grounding, strict module+section relevance is the more important setting.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_benchmark_table(rows: list[dict[str, str | float | int | bool]]) -> None:
    table = Table(title="Benchmark results")
    for key in rows[0].keys():
        table.add_column(key, justify="right" if key not in {"chunking", "retriever", "query_type"} else "left")
    for row in rows:
        table.add_row(*[f"{value:.3f}" if isinstance(value, float) else str(value) for value in row.values()])
    console.print(table)


if __name__ == "__main__":
    app()
