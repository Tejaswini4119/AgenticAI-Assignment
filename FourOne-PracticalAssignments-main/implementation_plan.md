# Implementation Plan - Agentic AI Assignment 1

This document outlines the design and implementation plan for the four practical tasks in **Agentic AI Assignment 1**.

## Goals & Requirements
The assignment consists of four tasks, each worth 5 marks (total 20 marks):
1. **LLM Workflow (5 Marks)**: Accept user input and generate a response using an LLM.
2. **Prompt Chaining (5 Marks)**: Multi-step LLM workflow: Topic $\rightarrow$ Summary $\rightarrow$ Extract Key Points $\rightarrow$ Produce 3 Questions.
3. **Agentic AI (5 Marks)**: Build a simple AI agent that accepts a task, plans the required steps, executes them using tools, and displays the final output.
4. **RAG-Based Question Answering (5 Marks)**: Retrieve relevant information from a PDF/TXT document and answer queries using an LLM.

## Directory Structure
We will organize the repository using clean folder separation, separating concerns for each task and sharing a common environment/configuration setup:

```
FourOne-PracticalAssignments/
├── README                     # Existing assignment prompt
├── requirements.txt           # Shared Python dependencies
├── .env.template              # Template for API keys
├── .env                       # Actual API keys (user-provided, gitignored)
├── task_1_llm_workflow/
│   ├── README.md              # Running instructions for Task 1
│   └── main.py                # Interactive CLI tool for LLM responses
├── task_2_prompt_chaining/
│   ├── README.md              # Running instructions for Task 2
│   └── main.py                # Multi-step Prompt Chaining script
├── task_3_agentic_ai/
│   ├── README.md              # Running instructions for Task 3
│   ├── agent.py               # Simple Plan-and-Execute/ReAct agent class
│   ├── tools.py               # Executable tools (calc, write_file, read_file)
│   └── main.py                # Command-line driver for Agent tasks
└── task_4_rag_qa/
    ├── README.md              # Running instructions for Task 4
    ├── documents/             # Folder for source PDF/TXT files
    │   └── attention_is_all_you_need.pdf # Default sample PDF file
    ├── rag.py                 # Retrieval & QA Pipeline (embedding, similarity, query)
    └── main.py                # Command-line interface for QA queries
```

---

## Technical Design

### Common LLM Client Wrapper
To avoid duplicating API initialization and to support different backends (Gemini, OpenAI, etc.), we will build a lightweight utility/wrapper. Since we are running in python 3.14, we will prioritize `google-generativeai` package for Gemini, or `openai` for OpenAI API.
We will write code that checks `.env` for:
- `GEMINI_API_KEY`: If set, uses Google's Gemini API (`gemini-2.5-flash`).
- `OPENAI_API_KEY`: If set, uses OpenAI API (`gpt-4o-mini`).

This makes the assignment fully portable and extremely easy for you (and your evaluator) to run.

---

### Task 1: LLM Workflow
- **Script**: `task_1_llm_workflow/main.py`
- **Behavior**:
  - Load environment variables from `.env`.
  - Prompt the user to enter their question/query.
  - Send the query to the configured LLM API.
  - Stream/print the response to the terminal.
  - Support an interactive loop where the user can continuously chat, or a single-shot execution.

---

### Task 2: Prompt Chaining
- **Script**: `task_2_prompt_chaining/main.py`
- **Behavior**:
  - Accept a input topic (or block of text) from the user.
  - **Step 1 (Summary)**: Pass the topic to the LLM with instructions to generate a concise summary.
  - **Step 2 (Key Points Extraction)**: Pass the summary from Step 1 to the LLM with instructions to extract exactly 5 key bullet points.
  - **Step 3 (Question Generation)**: Pass the key points from Step 2 to the LLM with instructions to generate 3 thought-provoking study/understanding questions.
  - Display the intermediate output of each stage with nice formatting.

---

### Task 3: Agentic AI
- **Scripts**:
  - `task_3_agentic_ai/tools.py`: Contains a set of Python functions representing tools (e.g., `calculate(expression)`, `write_file(filepath, content)`, `read_file(filepath)`).
  - `task_3_agentic_ai/agent.py`: Agent class implementing the planning and execution loop:
    1. **Plan**: Given a goal (e.g., "Calculate the 15th Fibonacci number, save it to `fib.txt`, and check the file"), ask the LLM to decompose the goal into a sequence of JSON steps, specifying which tool to run and with what arguments.
    2. **Execute**: Iterate through the steps, call the respective Python tool, and collect the output.
    3. **Verify/Refine**: If a tool fails, prompt the LLM to replan or fix.
    4. **Synthesize**: Pass the execution trace to the LLM to generate the final response.
  - `task_3_agentic_ai/main.py`: Interactive CLI to input a task and watch the agent plan and execute it step-by-step.

---

### Task 4: RAG-Based QA
- **Scripts**:
  - `task_4_rag_qa/rag.py`:
    - **Chunking**: Read TXT/PDF file and chunk into segments of ~500 characters with ~100 characters overlap.
    - **Embeddings**: Call the embedding API (e.g., Gemini's `text-embedding-004` or OpenAI's `text-embedding-3-small`) to generate vectors for each chunk.
    - **Retrieval**: Compute cosine similarity between the user's query embedding and the chunk embeddings. Retrieve top $K$ chunks.
    - **Generation**: Insert the retrieved context into a custom prompt and ask the LLM to answer the user's question based strictly on the context.
  - `task_4_rag_qa/main.py`: Indexing and querying CLI. When run, it indexes files in `documents/` and enters a query loop.

---

## User Review Required

> [!IMPORTANT]
> **API Key Setup**: You will need to provide a `GEMINI_API_KEY` (recommended) or `OPENAI_API_KEY` in a `.env` file at the root of the project to run the scripts.
>
> **Python Dependencies**: We will install lightweight python libraries (`google-generativeai`, `python-dotenv`, `pypdf`, `numpy`). Let us know if you have any constraints regarding installing pip packages.

---

## Verification Plan

### Automated Verification
We will write a test suite or verification script that runs each task with pre-configured prompts and checks:
1. LLM connectivity and response generation.
2. Prompt chaining steps producing summary, key points, and questions.
3. Agent planning and execution of math/file operations.
4. Document indexing, chunking, retrieval, and QA.

### Manual Verification
1. Run `python task_1_llm_workflow/main.py` and test general chat.
2. Run `python task_2_prompt_chaining/main.py` with a topic (e.g. "Photosynthesis") and check the structured output.
3. Run `python task_3_agentic_ai/main.py` with an agent task and observe the plan/execution output.
4. Run `python task_4_rag_qa/main.py` to ingest a text file and query it.
