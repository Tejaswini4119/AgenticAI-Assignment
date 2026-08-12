"""
Runs every question in examples/sample_questions.json through the pipeline
and writes a results report to examples/results.md. Useful for the
experiment write-up (put this table in your submission/report).

Usage:
    python evaluate.py
"""
import json
import time

from src.pipeline import TextToSQLPipeline

QUESTIONS_PATH = "examples/sample_questions.json"
OUTPUT_PATH = "examples/results.md"


def main():
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    pipeline = TextToSQLPipeline()
    rows = []
    for q in questions:
        start = time.time()
        result = pipeline.ask(q)
        elapsed = time.time() - start
        rows.append(
            {
                "question": q,
                "tables": ", ".join(result.retrieved_tables),
                "sql": (result.sql or "").replace("\n", " "),
                "attempts": result.attempts,
                "status": "OK" if result.success else f"FAILED: {result.error}",
                "rows_returned": len(result.result) if result.success else "-",
                "time_s": round(elapsed, 2),
            }
        )
        print(f"[{'OK' if result.success else 'FAIL'}] {q}")

    with open(OUTPUT_PATH, "w") as f:
        f.write("# Evaluation Results\n\n")
        f.write("| # | Question | Retrieved Tables | Attempts | Status | Rows | Time (s) |\n")
        f.write("|---|----------|-------------------|----------|--------|------|----------|\n")
        for i, r in enumerate(rows, 1):
            f.write(
                f"| {i} | {r['question']} | {r['tables']} | {r['attempts']} | "
                f"{r['status']} | {r['rows_returned']} | {r['time_s']} |\n"
            )
        f.write("\n## Generated SQL per question\n\n")
        for i, r in enumerate(rows, 1):
            f.write(f"**{i}. {r['question']}**\n\n```sql\n{r['sql']}\n```\n\n")

    print(f"\nWrote report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
