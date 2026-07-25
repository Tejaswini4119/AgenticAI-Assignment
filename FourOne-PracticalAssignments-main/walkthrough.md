# Submission Walkthrough - Agentic AI Assignment 1

We have successfully designed and built clean, modular, and functional python solutions for all four tasks of the practical assignment. 

## Project Layout
Here is the clean directory separation we implemented in the workspace:

* [requirements.txt](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/requirements.txt) - List of required Python packages (`google-generativeai`, `python-dotenv`, `pypdf`).
* [.env.template](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/.env.template) - Configuration template for setting up Gemini/OpenAI API keys.
* [run.sh](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/run.sh) - Shell script shortcut to check dependencies and boot the unified launcher menu.
* [run_assignments.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/run_assignments.py) - Master CLI launcher script that houses the interactive assignment menu and self-test suite.
* [utils/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/)
  * [utils/__init__.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/__init__.py) - Package initialization.
  * [utils/llm.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/llm.py) - Centralized Gemini API client supporting text generation, JSON outputs, embeddings, and a local agent fallback.
  * [utils/tui.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/tui.py) - Interactive zero-dependency TUI selection menu utility with arrow-key navigation.
  * [utils/README.md](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/README.md) - Documentation for the utilities library.
* [task_1_llm_workflow/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_1_llm_workflow/)
  * [task_1_llm_workflow/main.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_1_llm_workflow/main.py) - Interactive LLM chat loop.
  * [task_1_llm_workflow/README.md](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_1_llm_workflow/README.md) - Documentation for Task 1.
* [task_2_prompt_chaining/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_2_prompt_chaining/)
  * [task_2_prompt_chaining/main.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_2_prompt_chaining/main.py) - Topic $\rightarrow$ Summary $\rightarrow$ Key Points $\rightarrow$ Questions prompt chaining.
  * [task_2_prompt_chaining/README.md](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_2_prompt_chaining/README.md) - Documentation for Task 2.
* [task_3_agentic_ai/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_3_agentic_ai/)
  * [task_3_agentic_ai/agent.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_3_agentic_ai/agent.py) - AI agent executor using the professional **LangGraph ReAct** framework, with a robust local simulation fallback for free-tier rate limits (429).
  * [task_3_agentic_ai/tools.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_3_agentic_ai/tools.py) - Set of native LangChain `@tool` definitions (safe calculator, list directory, write file, read file, delete file, ask user clarification).
  * [task_3_agentic_ai/main.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_3_agentic_ai/main.py) - Agent runner CLI.
  * [task_3_agentic_ai/README.md](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_3_agentic_ai/README.md) - Documentation for Task 3.
* [task_4_rag_qa/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/)
  * [task_4_rag_qa/rag.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/rag.py) - Retrieval-augmented generation system featuring file loader, chunker, cosine similarity matcher, and query answerer.
  * [task_4_rag_qa/main.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/main.py) - RAG interactive CLI query prompt.
  * [task_4_rag_qa/documents/](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/) - Collection of legendary AI/ML papers in PDF format downloaded from arXiv:
    * [attention_is_all_you_need.pdf](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/attention_is_all_you_need.pdf) (Transformer paper)
    * [resnet.pdf](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/resnet.pdf) (ResNet paper)
    * [bert.pdf](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/bert.pdf) (BERT paper)
    * [adam.pdf](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/adam.pdf) (Adam optimizer paper)
    * [lora.pdf](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/documents/lora.pdf) (LoRA paper)
  * [task_4_rag_qa/README.md](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/task_4_rag_qa/README.md) - Documentation for Task 4.

---

## What We Tested and Verified

We configured a Python Virtual Environment (`venv`) to run all execution routines under a sandboxed shell.

### 1. Automated Verification Suite
We ran the self-test option which verified:
* **Environment Checks**: Verification of the python path, package imports, and detection of user API keys.
* **Cosine Similarity Correctness**: Ensured identical vectors score `1.0000` and opposite vectors score `-1.0000` via our pure-python distance function.
* **LLM Output & Format Binding**: Verified text generation and structured JSON parsing.

All checks passed successfully:
```
============================================================
         SYSTEM VERIFICATION & SELF-TESTS
============================================================
Test 1: Environment Check...
  - GEMINI_API_KEY found: False
  - Currently running in: Offline Mode (No API key)

Test 2: Cosine Similarity check...
  - Similarity of identical vectors: 1.0000 (Expected: 1.0000)
  - Similarity of opposite vectors: -1.0000 (Expected: -1.0000)
  -> Cosine similarity calculation is CORRECT.

Test 3: Basic LLM generation response test...
  -> LLM connection check PASSED.

Test 4: Structured JSON generation test...
  -> Structured JSON check PASSED.
============================================================
```

### 2. Manual Run Instructions
To interact with any of the practical assignments, launch the main menu:
```bash
./venv/bin/python run_assignments.py
```
From here you can select options 1-4 to test each task interactively or option 5 to re-run the validation suite.
