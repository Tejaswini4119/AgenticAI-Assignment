"""Executes generated SQL safely against the SQLite database."""
import re
import sqlite3

import pandas as pd

FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|PRAGMA|VACUUM)\b",
    re.IGNORECASE,
)


class UnsafeQueryError(Exception):
    pass


def is_read_only(sql: str) -> bool:
    return FORBIDDEN.search(sql) is None and sql.strip().lower().startswith(("select", "with"))


def execute_sql(sql: str, db_path: str) -> pd.DataFrame:
    """Runs a read-only query and returns the result as a DataFrame.

    Raises UnsafeQueryError for anything that isn't a plain SELECT/WITH,
    and sqlite3.Error (bubbled up) for syntax/semantic SQL errors so the
    caller can feed the message back to the LLM for self-repair.
    """
    if not is_read_only(sql):
        raise UnsafeQueryError(
            "Only read-only SELECT/WITH queries are allowed. Refused: " + sql
        )

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df
