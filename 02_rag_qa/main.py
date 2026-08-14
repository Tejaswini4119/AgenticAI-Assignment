"""
Experiment 2: RAG-Based Question Answering System

Indexing (indexer.py) + retrieval (retriever.py) + grounded response
generation (this file) over a small multi-document knowledge base:
a product FAQ, an employee handbook excerpt, and an onboarding guide.
Retrieval works across all three, so a query only pulls in the documents
actually relevant to it.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from indexer import load_or_build_index, build_index
from retriever import retrieve

SYSTEM_INSTRUCTION = (
    "You are a support assistant that answers questions using ONLY the "
    "provided context excerpts. Cite which document each fact comes from "
    "inline like (source: onboarding_guide.txt). If the context does not "
    "contain the answer, say so plainly instead of guessing."
)

LOW_CONFIDENCE_THRESHOLD = 0.55


def build_context(hits: list[dict]) -> str:
    parts = []
    for hit in hits:
        parts.append(f"[{hit['doc']} #{hit['chunk_id']}]\n{hit['text']}")
    return "\n\n".join(parts)


def answer_question(question: str, top_k: int = 4):
    hits = retrieve(question, top_k=top_k)
    context = build_context(hits)

    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    answer = llm.generate_text(prompt, system_instruction=SYSTEM_INSTRUCTION)

    return answer, hits


def print_sources(hits: list[dict]):
    print("\n[sources]")
    for hit in hits:
        flag = "" if hit["score"] >= LOW_CONFIDENCE_THRESHOLD else "  (low relevance)"
        print(f"  {hit['score']:.3f}  {hit['doc']} #{hit['chunk_id']}{flag}")


def main():
    print("=" * 70)
    print("  Experiment 2: RAG-Based Question Answering")
    print("=" * 70)
    print("Knowledge base: documents/product_faq.txt, employee_handbook.txt,")
    print("                onboarding_guide.txt")
    load_or_build_index()
    print("\nAsk a question. Type 'reindex' to rebuild the index, or")
    print("'exit'/'quit' to leave.\n")
    print("Try: 'what's the refund policy for Nimbus?'")
    print("     'how much PTO do I accrue per month?'")
    print("     'what equipment do new hires get?'\n")

    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                continue
            if question.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            if question.lower() == "reindex":
                build_index()
                continue

            answer, hits = answer_question(question)
            print(f"\n[answer]\n{answer}")
            print_sources(hits)
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
