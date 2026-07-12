from pathlib import Path
from pydantic import BaseModel

class AppConfig(BaseModel):
    raw_dir: Path = Path("data/raw")
    processed_chunks: Path = Path("data/processed/chunks.jsonl")
    chunk_size: int = 900
    chunk_overlap: int = 120
    top_k: int = 5
