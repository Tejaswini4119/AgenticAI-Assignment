# Experiment 4 — SQL Agent with Tool Use (ReAct)

Develop a **ReAct-based agent** using database tools — the model reasons
step by step, deciding at each turn whether to call a tool or answer,
rather than following a fixed pipeline.

## How this differs from Experiment 1

[Experiment 1](../01_text_to_sql) retrieves the relevant schema up front
(embedding similarity) and hands it to the LLM in one shot. This agent is
given **no schema at all** — it has to call `list_tables` and `get_schema`
itself, on its own initiative, before it can write a query. The number and
order of steps isn't fixed; the agent decides when it has enough
information to stop.

## Tools (`tools.py`)

| Tool | Does |
|---|---|
| `list_tables()` | Returns every table name in the database |
| `get_schema(table)` | Returns a table's column names/types |
| `run_sql(query)` | Executes a single read-only `SELECT`; rejects anything else |

## The ReAct loop (`agent.py`)

Each step, the model sees the full history of thoughts/actions/observations
and responds with exactly one JSON object:

```json
{"thought": "...", "call_tool": {"name": "get_schema", "args": {"table": "books"}}}
```
or, once it has enough information:
```json
{"thought": "...", "final_answer": "..."}
```

The loop runs for up to 8 steps, appends each observation to the running
history, and stops as soon as a `final_answer` appears (or the step limit
is hit, or the model returns something that matches neither shape — which
is treated as a protocol failure rather than looped on).

## Sample database

`seed_db.py` builds `library.db`: `authors`, `books`, `members`, `loans`
(loans with a `NULL` `return_date` are still checked out). A fresh domain
from experiment 1's company database, but with the same kind of
multi-table joins needed to answer non-trivial questions.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 04_sql_agent/main.py
```

Needs `GEMINI_API_KEY` (see `experiments/.env.template` — or the repo-root
`.env` / `assignment-agenticai/.env`, `common/llm.py` checks all three).
Structured tool-calling needs a real model; without a key the agent
correctly detects the offline stub doesn't match the tool-call protocol and
stops immediately rather than looping uselessly.

Try:
- `which books are currently on loan and not yet returned?`
- `who are the most active borrowers?`
- `how many books has each author written?`

## Files

| File | Purpose |
|---|---|
| `seed_db.py` | Creates and seeds `library.db` |
| `tools.py` | The three tools the agent can call, plus their text descriptions for the system prompt |
| `agent.py` | The ReAct loop: prompt → parse → dispatch tool → append observation → repeat |
| `main.py` | Interactive CLI, prints every thought/action/observation |

## Notes / limitations

- `run_sql` only permits statements starting with `SELECT` — the agent has
  no way to modify the database, by design.
- The agent isn't forced to call `list_tables`/`get_schema` before
  `run_sql`; it usually does because the system prompt tells it to, but a
  model that ignores that instruction will just get a SQL error back as an
  observation and can recover from there (or not, within the step budget).
- **Gemini's free tier caps `gemini-2.5-flash` at 20 requests/day** —
  `common/llm.py`'s mock fallback kicks in once that's exhausted, same as
  every other experiment in this repo. A single ReAct run here can easily
  use 3-6 of those 20 calls, so this is the fastest experiment to hit the
  ceiling.
