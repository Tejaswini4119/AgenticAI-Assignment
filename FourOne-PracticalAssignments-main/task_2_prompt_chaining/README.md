# Task 2: Prompt Chaining (5 Marks)

Implement a multi-step LLM workflow to generate a summary, extract key points, and produce three questions from a given topic.

## How it Works
1. **Input**: User inputs a topic of choice.
2. **Step 1 (Summary)**: An LLM call generates a summary based on the topic.
3. **Step 2 (Key Points)**: The generated summary is passed as context to a second LLM prompt to extract the top 5 key bullet points.
4. **Step 3 (Questions)**: The extracted key points are passed to a third LLM prompt to produce exactly three thought-provoking questions.
5. All intermediate steps and output data flows are logged to the terminal.

## Running Instructions
Run the script using the project's virtual environment:
```bash
./venv/bin/python task_2_prompt_chaining/main.py
```
Input any topic of interest when prompted.
