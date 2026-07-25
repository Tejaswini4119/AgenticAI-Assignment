import os
import sys
import json
from pypdf import PdfReader
from utils import llm

class RAGSystem:
    def __init__(self, index_file: str = "rag_index.json"):
        self.index_file = index_file
        self.chunks = []
        self.embeddings = []

    def extract_text(self, filepath: str) -> str:
        """
        Extracts text from a TXT or PDF file.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        else:
            raise ValueError(f"Unsupported file type '{ext}'. Only .txt and .pdf are supported.")

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 150) -> list[str]:
        """
        Chunks the input text into segments with overlapping bounds.
        """
        text = text.strip()
        if not text:
            return []
            
        # Clean double spacing/newlines to preserve quality chunks
        text = " ".join(text.split())
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks

    def build_index(self, filepath: str):
        """
        Loads document, chunks it, generates embeddings, and saves index.
        """
        print(f"[RAG] Extracting text from {os.path.basename(filepath)}...")
        raw_text = self.extract_text(filepath)
        
        print("[RAG] Chunking text...")
        self.chunks = self.chunk_text(raw_text)
        print(f"[RAG] Created {len(self.chunks)} chunks.")
        
        print("[RAG] Generating embeddings (this may take a few seconds)...")
        self.embeddings = []
        for i, chunk in enumerate(self.chunks):
            print(f"  Embedding chunk {i+1}/{len(self.chunks)}...", end="\r")
            emb = llm.get_embedding(chunk)
            self.embeddings.append(emb)
        print("\n[RAG] Embedding generation complete.")
        
        # Save to local cache
        self.save_index()

    def save_index(self):
        """
        Caches the built index to disk.
        """
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings
        }
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"[RAG] Saved index to cache: {self.index_file}")

    def load_index(self) -> bool:
        """
        Loads the cached index from disk if it exists.
        """
        if not os.path.exists(self.index_file):
            return False
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.chunks = data["chunks"]
            self.embeddings = data["embeddings"]
            return True
        except Exception as e:
            print(f"[RAG Error] Failed to load index: {e}")
            return False

    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[str, float]]:
        """
        Vector search to retrieve the top K chunks similar to the query.
        """
        if not self.chunks or not self.embeddings:
            raise ValueError("No document indexed. Build or load index first.")
            
        # Get query embedding
        query_emb = llm.get_embedding(query)
        
        # Compute similarities
        scored_chunks = []
        for chunk, emb in zip(self.chunks, self.embeddings):
            sim = llm.cosine_similarity(query_emb, emb)
            scored_chunks.append((chunk, sim))
            
        # Sort by similarity score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]

    def answer_query(self, query: str, top_k: int = 3) -> tuple[str, list[tuple[str, float]]]:
        """
        Retrieves context and asks LLM to answer the query.
        """
        retrieved = self.retrieve(query, top_k=top_k)
        
        # Build prompt context
        context_parts = []
        for idx, (chunk, score) in enumerate(retrieved):
            context_parts.append(f"--- Context Segment {idx+1} (Relevance Score: {score:.4f}) ---\n{chunk}")
            
        context_str = "\n\n".join(context_parts)
        
        # System instruction forces model to answer strictly based on the context
        system_instruction = (
            "You are a precise QA assistant. You are given a user question and some retrieved context. "
            "Your task is to answer the question accurately using ONLY the provided context. "
            "If the answer cannot be found in the context, respond exactly with: "
            "\"I cannot find the answer in the provided document.\"\n\n"
            "Do not use external knowledge or make assumptions."
        )
        
        prompt = (
            f"Context Information:\n{context_str}\n\n"
            f"User Question: {query}\n\n"
            f"Answer:"
        )
        
        answer = llm.generate_text(prompt, system_instruction=system_instruction)
        return answer, retrieved
