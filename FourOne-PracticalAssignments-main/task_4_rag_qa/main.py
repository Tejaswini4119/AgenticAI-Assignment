import os
import sys

# Ensure parent directory (project root) is in path so we can import utils.llm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_4_rag_qa.rag import RAGSystem
from utils.tui import interactive_select

def main():
    print("=" * 60)
    print("         Task 4: RAG-Based Question Answering")
    print("=" * 60)
    print("This system retrieves relevant text chunks from a TXT/PDF document")
    print("using vector search and answers queries based strictly on that document.")
    print("=" * 60)

    # Initialize RAG System
    index_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_index.json")
    rag = RAGSystem(index_file=index_file)

    # Load or build index
    if rag.load_index():
        print("[RAG] Loaded existing index from cache.")
        use_cached = input("Do you want to re-index the document? (y/N): ").strip().lower()
        reindex = use_cached == 'y'
    else:
        reindex = True

    if reindex:
        docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
        available_docs = []
        if os.path.exists(docs_dir):
            for f in os.listdir(docs_dir):
                if f.lower().endswith(('.txt', '.pdf')):
                    available_docs.append(f)
            available_docs.sort()

        # Place attention_is_all_you_need.pdf as the first item if present
        default_file = "attention_is_all_you_need.pdf"
        if default_file in available_docs:
            available_docs.remove(default_file)
            available_docs.insert(0, default_file)

        # Try TUI selection first
        tui_options = available_docs + ["[Enter a custom raw file path]"]
        selection_idx = interactive_select(tui_options, title="Select a Document for RAG:")
        
        doc_path = None
        if selection_idx != -1:
            if selection_idx == len(available_docs):
                doc_path = input("Enter custom raw path to TXT or PDF document: ").strip()
            else:
                doc_path = os.path.join(docs_dir, available_docs[selection_idx])
                print(f"Selected Document: {available_docs[selection_idx]}")
        else:
            # Fallback to standard numbered selection
            print("\nAvailable Documents in 'documents/' folder:")
            for idx, doc in enumerate(available_docs):
                print(f"  {idx + 1}. {doc}")
            print(f"  {len(available_docs) + 1}. [Enter a custom raw file path]")

            selection = input(f"\nSelect a document (1-{len(available_docs) + 1}) [Default: 1]: ").strip()

            if not selection or selection == "1":
                if available_docs:
                    doc_path = os.path.join(docs_dir, available_docs[0])
                else:
                    doc_path = input("Enter path to TXT or PDF document: ").strip()
            elif selection.isdigit() and 1 <= int(selection) <= len(available_docs):
                doc_path = os.path.join(docs_dir, available_docs[int(selection) - 1])
            elif selection == str(len(available_docs) + 1):
                doc_path = input("Enter custom raw path to TXT or PDF document: ").strip()
            else:
                print("Invalid selection. Using default document.")
                if available_docs:
                    doc_path = os.path.join(docs_dir, available_docs[0])
                else:
                    doc_path = input("Enter path to TXT or PDF document: ").strip()

        if not doc_path or not os.path.exists(doc_path):
            print(f"Error: File '{doc_path}' not found. Exiting.")
            return

        try:
            rag.build_index(doc_path)
        except Exception as e:
            print(f"Failed to build index: {e}")
            return

    print("\nRAG System Ready. Type 'exit', 'quit', or 'q' to end the session.\n")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting RAG. Goodbye!")
                break

            print("\nSearching and generating answer...")
            answer, retrieved = rag.answer_query(query, top_k=2)

            print("\n" + "-" * 50)
            print("RETRIEVED CONTEXT SEGMENTS:")
            print("-" * 50)
            for idx, (chunk, score) in enumerate(retrieved):
                print(f"[{idx+1}] Score: {score:.4f} | Content: {chunk[:120]}...")
            print("-" * 50)
            
            print("\n" + "=" * 50)
            print("ANSWER:")
            print("=" * 50)
            print(answer)
            print("=" * 50)

        except KeyboardInterrupt:
            print("\nExiting RAG. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
