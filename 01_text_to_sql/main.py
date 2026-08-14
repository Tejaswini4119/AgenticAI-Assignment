"""
Experiment 1: Text-to-SQL Workflow

End-to-end pipeline: natural-language question -> schema retrieval (embed +
cosine similarity over table descriptions) -> LLM-generated SQL -> execution
against a real SQLite database -> one self-repair attempt if the query
errors -> a natural-language answer grounded in the returned rows.
"""
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
import seed_db
from retriever import retrieve_tables, schema_context_for
from schema_catalog import TABLES, to_ddl_snippet

SYSTEM_INSTRUCTION = (
    "You are a careful SQLite SQL generator. You are given a subset of a "
    "database schema and a natural-language question. Respond ONLY with a "
    "JSON object of the form {\"sql\": \"<single SQLite SELECT statement>\", "
    "\"explanation\": \"<one sentence on the approach>\"}. "
    "Only reference tables/columns you were given. Never write INSERT, "
    "UPDATE, DELETE or DDL statements -- read-only queries only."
)


def generate_sql(question: str, schema_context: str, prior_error: str = None) -> dict:
    prompt = f"Schema:\n{schema_context}\n\nQuestion: {question}"
    if prior_error:
        prompt += (
            f"\n\nYour previous SQL failed to execute with this error:\n{prior_error}\n"
            "Fix the query and try again."
        )
    return llm.generate_json(prompt, system_instruction=SYSTEM_INSTRUCTION)


def run_query(db_path: str, sql: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        return columns, rows
    finally:
        conn.close()


def print_rows(columns, rows):
    if not columns:
        print("(no result columns)")
        return
    widths = [max(len(c), *(len(str(r[i])) for r in rows)) if rows else len(c) for i, c in enumerate(columns)]
    header = " | ".join(c.ljust(w) for c, w in zip(columns, widths))
    print(header)
    print("-" * len(header))
    for r in rows[:20]:
        print(" | ".join(str(r[i]).ljust(w) for i, w in enumerate(widths)))
    if len(rows) > 20:
        print(f"... ({len(rows) - 20} more rows)")


def answer_from_rows(question: str, columns, rows) -> str:
    if not rows:
        return "No matching rows were found."
    sample = [dict(zip(columns, r)) for r in rows[:15]]
    prompt = (
        f"Question: {question}\nQuery result rows (JSON): {sample}\n"
        "In one or two sentences, answer the question using only this data."
    )
    return llm.generate_text(prompt)


def handle_question(db_path: str, question: str):
    retrieved = retrieve_tables(question, top_k=4)
    print(f"\n[retrieval] Selected tables: {', '.join(retrieved)}")
    schema_context = schema_context_for(retrieved)

    result = generate_sql(question, schema_context)
    sql = result.get("sql", "")
    print(f"[generation] {result.get('explanation', '')}")
    print(f"[sql]\n{sql}\n")

    try:
        columns, rows = run_query(db_path, sql)
    except sqlite3.Error as e:
        print(f"[execution] Query failed: {e}\n[repair] Asking the model to fix it...")
        result = generate_sql(question, schema_context, prior_error=str(e))
        sql = result.get("sql", "")
        print(f"[sql - repaired]\n{sql}\n")
        columns, rows = run_query(db_path, sql)

    print_rows(columns, rows)
    print(f"\n[answer] {answer_from_rows(question, columns, rows)}")


def print_full_schema():
    for table in TABLES:
        print(to_ddl_snippet(table))
        print()


def main():
    print("=" * 70)
    print("  Experiment 1: Text-to-SQL Workflow (retrieval + query generation)")
    print("=" * 70)
    db_path = seed_db.build()
    print(f"Sample database ready at: {db_path}")
    print("Ask questions in plain English. Type 'schema' to see all tables,")
    print("or 'exit'/'quit' to leave.\n")
    print("Try: 'who are our top 3 customers by total spend?'")
    print("     'which products have fewer than 50 units in stock?'")
    print("     'what is the average salary in the Sales department?'\n")

    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                continue
            if question.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            if question.lower() == "schema":
                print_full_schema()
                continue

            handle_question(db_path, question)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
