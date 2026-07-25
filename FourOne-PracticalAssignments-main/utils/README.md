# Utilities Library

This directory contains the central helper modules utilized across all four assignment tasks.

## Modules

### 1. [llm.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/llm.py)
A wrapper for the Gemini API (using the direct `google-generativeai` client):
- **Text Generation**: `generate_text(prompt, system_instruction)` generates natural language responses.
- **JSON Formatting**: `generate_json(prompt, system_instruction)` returns structured dict outputs.
- **Vector Embeddings**: `get_embedding(text)` returns 768-dimensional document vectors.
- **Cosine Similarity**: `cosine_similarity(v1, v2)` performs pure-python vector angle comparisons.
- **Local Agent Fallback**: Automatically intercepts API exhaustion (429) errors and routes requests to the local agent pipeline.

### 2. [tui.py](file:///home/sicmundus/Desktop/Dev/FourOne-PracticalAssignments/utils/tui.py)
A keyboard-interactive selection selector module:
- **Arrow-Key Selector**: Provides an interactive terminal UI for navigating choices using keyboard arrow keys.
- **Clean Display**: Clears itself from terminal buffers upon choice selection.
- **Numbered Fallback**: Gracefully falls back to standard numbered input menus in non-TTY terminals (e.g., automated test run environments).
