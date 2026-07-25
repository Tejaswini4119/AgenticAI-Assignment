# Task 3: Agentic AI (5 Marks)

Build a simple AI agent that accepts a task, plans the required steps, executes them, and displays the final output.

## How it Works
1. **ReAct Loop**: The agent utilizes a Reasoning-and-Acting (ReAct) loop.
2. **Tools**: The agent has access to specific tools defined in `tools.py`:
   - `calculate(expression)`: Safe python evaluation of simple math.
   - `write_file(filename, content)`: Writes to a workspace file.
   - `read_file(filename)`: Reads from a workspace file.
   - `get_current_time()`: Gets system date and time.
3. **Execution Steps**:
   - The user inputs a task description.
   - The agent sends the task to the LLM.
   - The LLM responds in JSON choosing to call a tool or finish the task.
   - If calling a tool, the agent executes it, collects the result (observation), and appends it to the history.
   - The agent repeats until it decides the task is done, then outputs the final results.

## Running Instructions
Run the agent CLI:
```bash
./venv/bin/python task_3_agentic_ai/main.py
```
Choose from the predefined options or write your own custom task!
