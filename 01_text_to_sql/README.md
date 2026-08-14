# Experiment 1 — Text-to-SQL Workflow

Build an end-to-end LLM workflow with **retrieval** and **query generation**:
turn a plain-English question into a SQL query, run it against a real
database, and answer the question from the results.

## Pipeline

```
question
   │
   ▼
1. Schema retrieval   — embed the question, cosine-similarity against
   (retriever.py)        pre-embedded table descriptions, keep top-k tables
   │
   ▼
2. SQL generation      — LLM sees only the retrieved schema + question,
   (main.py)              returns {"sql": ..., "explanation": ...}
   │
   ▼
3. Execution            — run the SQL against SQLite
   │
   ├─ error? ──▶ 4. Self-repair — feed the error back to the LLM once,
   │               retry execution with the corrected query
   ▼
5. Answer generation    — LLM turns the result rows into a one/two
                           sentence natural-language answer
```

The retrieval step is the interesting part: rather than always pasting the
whole schema into the prompt (fine here with 6 tables, unworkable on a
warehouse with hundreds), each table's description is embedded once and
cached (`schema_index.json`). At query time only the top-k most relevant
tables are pulled into context — e.g. asking about customer spend retrieves
`customers`, `orders`, `order_items`, `products` but not `employees` or
`departments`.

## Sample database

`seed_db.py` creates `company.db` (SQLite) on first run with 6 tables:
`customers`, `products`, `orders`, `order_items`, `employees`,
`departments` — enough relational structure (joins, foreign keys) to make
retrieval and multi-table SQL generation meaningful. Delete `company.db` or
run `python seed_db.py` to rebuild it from scratch.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 01_text_to_sql/main.py
```

Needs `GEMINI_API_KEY` set in the repo-root `.env` (see `.env.template`).
Without a key the LLM calls fall back to an offline mock so the script still
runs, but SQL generation and answers will just be stub text.

Try:
- `who are our top 3 customers by total spend?`
- `which products have fewer than 50 units in stock?`
- `what is the average salary in the Sales department?`
- `schema` — print the full table catalog
- `exit` — quit

## Files

| File | Purpose |
|---|---|
| `schema_catalog.py` | Table/column metadata + descriptions used for retrieval and prompting |
| `seed_db.py` | Creates and seeds `company.db` |
| `retriever.py` | Embeds table descriptions, caches them, retrieves top-k relevant tables per question |
| `main.py` | CLI: retrieval → SQL generation → execution → self-repair → NL answer |

## Notes / limitations

- Retrieval quality depends entirely on how well each table's description
  captures what questions it can answer — a table described too tersely
  will be under-retrieved (see the code comment on why `order_items`'
  description explicitly mentions revenue/best-sellers).
- The self-repair loop only retries once; a query that fails twice in a row
  is surfaced as an error rather than looped on indefinitely.
- The LLM is instructed to emit read-only `SELECT` statements only.
