# Task 4: RAG-Based Question Answering (5 Marks)

Develop a basic RAG application that retrieves relevant information from a PDF/TXT document and answers user queries using an LLM.

## How it Works
1. **Document Loading**: Supports both plain `.txt` and `.pdf` files (using `pypdf`).
2. **Text Chunking**: Breaks the document text into overlaps (default 600 characters size, 150 characters overlap) to preserve semantic contexts.
3. **Embeddings & Indexing**: Generates text embeddings using Gemini's API (`models/text-embedding-004`) and saves the index cached to a JSON file (`rag_index.json`).
4. **Vector Retrieval**: Accepts a user query, embeds it, calculates cosine similarity in pure Python with all chunk vectors, and extracts the top $K$ context matches.
5. **Contextual Generation**: Passes the retrieved context and user query into the LLM under instructions to only answer if the answer is present in the context, preventing hallucinations.

## Running Instructions
Run the RAG interface:
```bash
./venv/bin/python task_4_rag_qa/main.py
```
You can press Enter to use the default `documents/attention_is_all_you_need.pdf` or supply your own PDF or TXT file path.
