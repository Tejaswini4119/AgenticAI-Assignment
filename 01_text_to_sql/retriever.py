"""
Retrieval step of the Text-to-SQL workflow.

Instead of always stuffing the LLM prompt with every table in the database
(fine for 6 tables, unworkable for a real warehouse with hundreds), we embed
a natural-language description of each table once, cache the vectors, and at
query time retrieve only the top-k tables most relevant to the user's
question. This mirrors how production text-to-SQL systems do schema linking
over large catalogs.
"""
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from schema_catalog import TABLES, to_retrieval_doc, get_table

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_index.json")


def _build_index() -> dict:
    index = {}
    for table in TABLES:
        doc = to_retrieval_doc(table)
        index[table["name"]] = {"doc": doc, "embedding": llm.get_embedding(doc)}
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f)
    return index


def load_or_build_index() -> dict:
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH) as f:
            cached = json.load(f)
        # Rebuild if the catalog has drifted (tables added/removed) since caching.
        if set(cached.keys()) == {t["name"] for t in TABLES}:
            return cached
    print("[retriever] Building schema embedding index (first run)...")
    return _build_index()


def retrieve_tables(question: str, top_k: int = 3) -> list[str]:
    """Return the top_k table names most relevant to the question."""
    index = load_or_build_index()
    q_embedding = llm.get_embedding(question)

    scored = [
        (name, llm.cosine_similarity(q_embedding, entry["embedding"]))
        for name, entry in index.items()
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [name for name, _score in scored[:top_k]]


def schema_context_for(table_names: list[str]) -> str:
    """Render DDL-style context for the given tables, for the LLM prompt."""
    from schema_catalog import to_ddl_snippet
    return "\n\n".join(to_ddl_snippet(get_table(name)) for name in table_names)


if __name__ == "__main__":
    q = "which customers signed up most recently"
    picked = retrieve_tables(q)
    print(f"Question: {q}\nRetrieved tables: {picked}")
