"""
Indexing step of the RAG pipeline: load every document in documents/,
chunk it, embed each chunk, and cache the result to rag_index.json.

Supports .txt directly and .pdf if pypdf is installed (optional dependency,
mirrors the pattern used in assignment-agenticai/task_4_rag_qa).
"""
import os
import sys
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(HERE, "documents")
INDEX_PATH = os.path.join(HERE, "rag_index.json")

CHUNK_SIZE = 600
CHUNK_OVERLAP = 120


def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("Install pypdf to index PDF files: pip install pypdf")
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def _documents_fingerprint() -> str:
    """Hash of filenames + contents, used to detect when documents/ changed."""
    h = hashlib.sha256()
    for name in sorted(os.listdir(DOCS_DIR)):
        path = os.path.join(DOCS_DIR, name)
        if os.path.isfile(path):
            h.update(name.encode())
            h.update(open(path, "rb").read())
    return h.hexdigest()


def build_index() -> list[dict]:
    print("[indexer] Building index from documents/ ...")
    entries = []
    for name in sorted(os.listdir(DOCS_DIR)):
        path = os.path.join(DOCS_DIR, name)
        if not os.path.isfile(path):
            continue
        text = extract_text(path)
        chunks = chunk_text(text)
        print(f"  {name}: {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            entries.append({
                "doc": name,
                "chunk_id": i,
                "text": chunk,
                "embedding": llm.get_embedding(chunk),
            })

    with open(INDEX_PATH, "w") as f:
        json.dump({"fingerprint": _documents_fingerprint(), "entries": entries}, f)
    return entries


def load_or_build_index() -> list[dict]:
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH) as f:
            cached = json.load(f)
        if cached.get("fingerprint") == _documents_fingerprint():
            return cached["entries"]
        print("[indexer] documents/ changed since last index; rebuilding.")
    return build_index()


if __name__ == "__main__":
    entries = build_index()
    print(f"Indexed {len(entries)} chunks across "
          f"{len({e['doc'] for e in entries})} documents.")
