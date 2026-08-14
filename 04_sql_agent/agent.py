"""
Experiment 4: SQL Agent with Tool Use

A ReAct-style agent: at each step the LLM sees the running history of
thoughts/actions/observations and decides whether to call a tool or give a
final answer. Unlike experiment 1's fixed retrieve -> generate -> execute
pipeline, there's no predetermined number of steps or order of operations
here -- the agent decides when it has enough information.
"""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from tools import TOOL_MAP, TOOL_SPECS

SYSTEM_INSTRUCTION = f"""\
You are a ReAct agent that answers questions about a SQLite database by \
calling tools. You do not know the schema in advance -- use list_tables \
and get_schema to discover it before writing SQL.

Available tools:
{TOOL_SPECS}

At every step, respond with ONLY a JSON object in one of these two forms:
1. To call a tool:   {{"thought": "<reasoning>", "call_tool": {{"name": "<tool>", "args": {{...}}}}}}
2. To finish:        {{"thought": "<reasoning>", "final_answer": "<answer to the user>"}}

Call exactly one tool per step. Only use run_sql after you have confirmed \
the relevant table names and columns with list_tables/get_schema. Give a \
final_answer as soon as you have enough information -- do not keep \
querying once you can already answer the question.\
"""


class SQLReActAgent:
    def __init__(self, max_steps: int = 8, on_step=None):
        self.max_steps = max_steps
        self.on_step = on_step or (lambda **kwargs: None)

    def _build_prompt(self, question: str, history: list[dict]) -> str:
        parts = [f"Question: {question}", "\nHistory so far:"]
        if not history:
            parts.append("(none yet -- this is your first step)")
        for entry in history:
            parts.append(entry)
        parts.append("\nWhat is your next step? Respond with the JSON object only.")
        return "\n".join(parts)

    def run(self, question: str) -> str:
        history: list[str] = []

        for step in range(1, self.max_steps + 1):
            prompt = self._build_prompt(question, history)
            response = llm.generate_json(prompt, system_instruction=SYSTEM_INSTRUCTION)

            if "final_answer" not in response and "call_tool" not in response:
                self.on_step(step=step, thought=None, error=(
                    "Model did not return a valid tool-call or final-answer "
                    f"(got: {response}). Stopping."
                ))
                return "Agent stopped: the model did not follow the tool-calling protocol."

            thought = response.get("thought", "")

            if "final_answer" in response:
                self.on_step(step=step, thought=thought, final_answer=response["final_answer"])
                return response["final_answer"]

            call = response["call_tool"]
            tool_name = call.get("name")
            tool_args = call.get("args", {})

            if tool_name not in TOOL_MAP:
                observation = f"Error: unknown tool '{tool_name}'. Available: {list(TOOL_MAP)}"
            else:
                try:
                    observation = TOOL_MAP[tool_name](**tool_args)
                except Exception as e:
                    observation = f"Error calling '{tool_name}': {e}"

            self.on_step(step=step, thought=thought, tool=tool_name, args=tool_args, observation=observation)

            history.append(f"Step {step} thought: {thought}")
            history.append(f"Step {step} action: called {tool_name}({tool_args})")
            history.append(f"Step {step} observation: {observation}")

        return "Agent stopped: reached the maximum number of steps without a final answer."
