"""
Retrieval step of the RAG pipeline: embed the query and rank all indexed
chunks by cosine similarity, across every document in the knowledge base.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from indexer import load_or_build_index


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    entries = load_or_build_index()
    q_embedding = llm.get_embedding(query)

    scored = []
    for entry in entries:
        score = llm.cosine_similarity(q_embedding, entry["embedding"])
        scored.append({**entry, "score": score})

    scored.sort(key=lambda e: e["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    q = "how many sick days do employees get?"
    for hit in retrieve(q):
        print(f"[{hit['score']:.3f}] {hit['doc']} #{hit['chunk_id']}: {hit['text'][:80]}...")
