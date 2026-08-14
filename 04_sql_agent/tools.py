"""
Database tools available to the ReAct agent. Deliberately no LLM code here
-- each function is a plain Python call against library.db that returns a
string observation, exactly what the agent will see in its scratchpad.

Unlike experiment 1 (where the schema is retrieved and handed to the LLM up
front), the agent here starts knowing nothing about the database and must
call list_tables / get_schema itself before it can write a useful query.
"""
import sqlite3

import seed_db

DB_PATH = seed_db.build()


def list_tables(**_) -> str:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return ", ".join(r[0] for r in rows)
    finally:
        conn.close()


def get_schema(table: str = "", **_) -> str:
    if not table:
        return "Error: 'table' argument is required."
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        if not rows:
            return f"Error: table '{table}' does not exist."
        cols = ", ".join(f"{r[1]} {r[2]}" for r in rows)
        return f"{table}({cols})"
    except sqlite3.Error as e:
        return f"Error: {e}"
    finally:
        conn.close()


def run_sql(query: str = "", **_) -> str:
    if not query:
        return "Error: 'query' argument is required."
    stripped = query.strip().lower()
    if not stripped.startswith("select"):
        return "Error: only SELECT statements are allowed."

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()
        if not rows:
            return "(no rows returned)"
        columns = [d[0] for d in cur.description]
        lines = [", ".join(columns)]
        for row in rows[:20]:
            lines.append(", ".join(str(v) for v in row))
        if len(rows) > 20:
            lines.append(f"... ({len(rows) - 20} more rows)")
        return "\n".join(lines)
    except sqlite3.Error as e:
        return f"Error: {e}"
    finally:
        conn.close()


TOOL_MAP = {
    "list_tables": list_tables,
    "get_schema": get_schema,
    "run_sql": run_sql,
}

TOOL_SPECS = """\
- list_tables(): returns the names of all tables in the database.
- get_schema(table): returns the column names/types for the given table.
- run_sql(query): executes a single read-only SELECT statement and returns \
the result rows, or an error message if the query is invalid.\
"""
