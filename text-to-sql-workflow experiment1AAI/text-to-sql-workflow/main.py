"""
CLI for the Text-to-SQL workflow.

Usage:
    python main.py                      # interactive REPL
    python main.py "your question"      # single question, one-shot
"""
import sys

from src.pipeline import TextToSQLPipeline


def print_result(result):
    print(f"\nRetrieved tables: {', '.join(result.retrieved_tables)}")
    print(f"Attempts: {result.attempts}")
    if result.sql:
        print(f"\nGenerated SQL:\n{result.sql}")
    if result.success:
        print(f"\nResult ({len(result.result)} rows):")
        print(result.result.to_string(index=False) if not result.result.empty else "(no rows)")
    else:
        print(f"\nFailed: {result.error}")


def main():
    pipeline = TextToSQLPipeline()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result = pipeline.ask(question)
        print_result(result)
        return

    print("Text-to-SQL workflow. Type a question, or 'quit' to exit.")
    while True:
        question = input("\n> ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        result = pipeline.ask(question)
        print_result(result)


if __name__ == "__main__":
    main()
