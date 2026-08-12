"""
Schema retrieval (the 'R' in this RAG-style Text-to-SQL pipeline).

Large databases can have far more tables than fit comfortably in an LLM
prompt. Instead of always dumping the *entire* schema, we embed each table's
metadata as a text "document" and retrieve only the top-k tables most
relevant to the user's question.

Two backends are supported:
  - OpenAIEmbeddingRetriever: uses OpenAI's embeddings API (semantic).
  - TfidfRetriever: pure local sklearn TF-IDF + cosine similarity, no API
    key required. Used automatically when EMBEDDING_MODEL is unset, so the
    project still runs end-to-end for retrieval even without any API key.
"""
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import settings
from .db import TableInfo, load_schema


class BaseRetriever:
    def __init__(self, tables: List[TableInfo]):
        self.tables = tables
        self.documents = [t.as_document() for t in tables]

    def retrieve(self, question: str, top_k: int) -> List[TableInfo]:
        raise NotImplementedError


class TfidfRetriever(BaseRetriever):
    """Local, free, deterministic retriever based on TF-IDF cosine similarity."""

    def __init__(self, tables: List[TableInfo]):
        super().__init__(tables)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def retrieve(self, question: str, top_k: int) -> List[TableInfo]:
        query_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked_idx = np.argsort(-scores)
        top_k = min(top_k, len(self.tables))
        return [self.tables[i] for i in ranked_idx[:top_k]]


class OpenAIEmbeddingRetriever(BaseRetriever):
    """Semantic retriever backed by the OpenAI embeddings API."""

    def __init__(self, tables: List[TableInfo], client, model: str):
        super().__init__(tables)
        self.client = client
        self.model = model
        self.doc_embeddings = self._embed(self.documents)

    def _embed(self, texts: List[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return np.array([d.embedding for d in resp.data])

    def retrieve(self, question: str, top_k: int) -> List[TableInfo]:
        query_emb = self._embed([question])
        scores = cosine_similarity(query_emb, self.doc_embeddings).flatten()
        ranked_idx = np.argsort(-scores)
        top_k = min(top_k, len(self.tables))
        return [self.tables[i] for i in ranked_idx[:top_k]]


def build_retriever(db_path: str = None) -> BaseRetriever:
    """Factory: picks the embedding retriever if configured, else TF-IDF."""
    tables = load_schema(db_path)

    if settings.embedding_model and settings.openai_api_key:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        return OpenAIEmbeddingRetriever(tables, client, settings.embedding_model)

    return TfidfRetriever(tables)
