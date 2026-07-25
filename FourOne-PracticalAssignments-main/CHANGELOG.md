# Changelog

All notable changes to the practical assignments codebase are documented here.

## [1.0.0] - 2026-07-16

### Added
- **Unified Task Launcher**: Created `run.sh` script at the root directory to handle dependency checks and boot the interactive TUI menu.
- **Interactive TUI**: Built `utils/tui.py` to provide a zero-dependency arrow-key menu selector with clean terminal history updates and standard numbered fallback for non-TTY shells.
- **LangGraph Framework**: Integrated `langchain` and `langgraph` in Task 3 (`task_3_agentic_ai/`) to replace custom parsing loops with the official LangGraph ReAct executor.
- **Local Agent Fallback Pipeline**: Implemented auto-detection of rate limits (429 errors) in `utils/llm.py` and `task_3_agentic_ai/agent.py`. It falls back to a local agent loop that parses user note inputs dynamically using regex and executes the tools.
- **Legendary AI/ML Papers**: Downloaded five standard research papers (Transformer, ResNet, BERT, Adam, and LoRA) to `task_4_rag_qa/documents/` for testing RAG.
- **Smart File Picker**: Enabled dynamic workspace file picker menus in the launcher and the RAG main CLI.
- **Utilities Documentation**: Added a dedicated `utils/README.md` file to document helper models and TUI selectors.

### Removed
- Removed the placeholder `sample.txt` file from the workspace.
