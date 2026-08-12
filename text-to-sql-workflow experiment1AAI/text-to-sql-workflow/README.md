# Text-to-SQL Workflow — Retrieval + Query Generation

**Course/Subject:** Agentic AI — Experiment 1
**Topic:** Build an end-to-end LLM workflow with retrieval and query generation

## 1. Aim

To design and implement an end-to-end agentic workflow that converts a
natural-language question into a correct SQL query, executes it against a
real database, and self-corrects when the generated query fails — combining
**retrieval** (schema linking) with **generation** (LLM-based SQL synthesis).

## 2. Problem

Feeding an LLM a user's question plus the *entire* database schema works for
toy databases, but breaks down for real ones (hundreds of tables blow the
context window and distract the model with irrelevant tables). This
experiment implements a **RAG-style Text-to-SQL pipeline**: retrieve only the
schema relevant to the question, then generate SQL grounded in that
retrieved context, then execute and self-repair on failure.

## 3. Architecture

```
                ┌─────────────────────┐
                │   User Question      │
                └──────────┬───────────┘
                           │
                           ▼
  ┌────────────────────────────────────────────┐
  │  1. RETRIEVAL (schema linking)              │
  │  - Introspect SQLite schema (tables, cols,  │
  │    FKs, sample rows)                        │
  │  - Embed each table as a text document      │
  │  - Rank tables by similarity to the question│
  │    (TF-IDF locally, or OpenAI embeddings)   │
  │  - Return top-k most relevant tables        │
  └──────────────────────┬───────────────────────┘
                           │ retrieved schema (top-k tables)
                           ▼
  ┌────────────────────────────────────────────┐
  │  2. GENERATION (LLM)                        │
  │  - Prompt = system rules + few-shot example │
  │    + retrieved schema + question            │
  │  - GPT-4o generates a SELECT/WITH query     │
  └──────────────────────┬───────────────────────┘
                           │ SQL
                           ▼
  ┌────────────────────────────────────────────┐
  │  3. EXECUTION (guarded)                     │
  │  - Reject anything that isn't read-only     │
  │  - Run against SQLite, return a DataFrame   │
  └──────────────────────┬───────────────────────┘
                           │
                on failure │ error message
                           ▼
  ┌────────────────────────────────────────────┐
  │  4. SELF-REPAIR (agentic loop)              │
  │  - Feed the SQL error back to the LLM       │
  │  - Regenerate, retry (bounded attempts)     │
  └────────────────────────────────────────────┘
                           │
                           ▼
                  Result table + SQL shown to user
```

## 4. Tech stack

| Component        | Choice                                            |
|-------------------|---------------------------------------------------|
| LLM (generation)  | OpenAI GPT-4o (`openai` SDK)                       |
| Retrieval         | scikit-learn TF-IDF (default, no key needed) or OpenAI embeddings |
| Database          | SQLite (auto-generated sample "company" DB)        |
| Orchestration     | Plain Python (`src/pipeline.py`)                   |
| Demo UI           | Streamlit                                          |
| Tests             | pytest                                             |

## 5. Project structure

```
text-to-sql-workflow/
├── data/
│   ├── build_database.py   # generates the sample SQLite DB
│   └── company.db          # pre-built sample database (checked in)
├── src/
│   ├── config.py           # env/config loading
│   ├── db.py                # schema introspection
│   ├── retriever.py         # RAG retrieval (TF-IDF / OpenAI embeddings)
│   ├── generator.py         # LLM prompt + SQL generation
│   ├── executor.py          # safe, read-only SQL execution
│   └── pipeline.py          # orchestrates retrieve -> generate -> execute -> repair
├── examples/
│   └── sample_questions.json
├── tests/
│   └── test_pipeline.py    # tests retrieval/execution without needing an API key
├── main.py                 # CLI
├── app_streamlit.py        # Streamlit demo UI
├── evaluate.py              # batch-runs sample_questions.json -> examples/results.md
├── requirements.txt
├── .env.example
└── README.md
```

## 6. Sample database schema

A fictional retail company with 6 tables and realistic foreign keys:

- `departments (department_id, name, location)`
- `employees (employee_id, first_name, last_name, email, department_id, hire_date, salary, manager_id)`
- `customers (customer_id, first_name, last_name, email, city, country, signup_date)`
- `products (product_id, name, category, unit_price, stock_quantity)`
- `orders (order_id, customer_id, employee_id, order_date, status)`
- `order_items (order_item_id, order_id, product_id, quantity, unit_price)`

Regenerate it any time with:
```bash
python data/build_database.py
```

## 7. Setup

```bash
git clone <this-repo-url>
cd text-to-sql-workflow
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
```

## 8. Usage

**CLI, one-shot:**
```bash
python main.py "What are the top 5 best-selling products by revenue?"
```

**CLI, interactive:**
```bash
python main.py
```

**Streamlit demo:**
```bash
streamlit run app_streamlit.py
```

**Batch evaluation (for the experiment report):**
```bash
python evaluate.py
# writes examples/results.md with every sample question, its SQL, and outcome
```

## 9. Retrieval without an API key

Schema retrieval works fully offline by default (TF-IDF), so `tests/`,
`data/build_database.py`, and the retrieval layer can all be verified without
any API key. Only the **generation** step (`src/generator.py`) requires
`OPENAI_API_KEY`, since that's the step that actually calls the LLM.

To switch retrieval to OpenAI embeddings instead of TF-IDF, set
`EMBEDDING_MODEL=text-embedding-3-small` in `.env`.

## 10. Design notes / what makes this "agentic"

- **Grounded generation**: the LLM never sees the full schema, only what
  retrieval selected — reducing hallucinated table/column names.
- **Guardrails**: `executor.py` rejects any non-`SELECT`/`WITH` statement
  before it ever touches the database.
- **Self-repair loop**: on a SQL execution error, the error message is fed
  back into a new generation call (bounded by `MAX_REPAIR_ATTEMPTS`), so the
  agent can recover from small mistakes (wrong column name, bad join) without
  human intervention.

## 11. Possible extensions

- Add a vector database (e.g. Chroma/FAISS) for retrieval at larger schema scale.
- Add a result-validation step (e.g. an LLM judge checking the answer matches intent).
- Support Postgres/MySQL via SQLAlchemy instead of SQLite.
- Add conversation memory for multi-turn follow-up questions.

## 12. Result

Running `evaluate.py` against the 10 sample questions in
`examples/sample_questions.json` produces `examples/results.md`, showing for
each question: the tables retrieval selected, the generated SQL, whether it
executed successfully (with self-repair attempts if needed), and the number
of rows returned. Paste that table into your experiment submission as the
"Output/Result" section.

## 13. Conclusion

This experiment demonstrates a minimal but complete agentic workflow: a
retrieval step that grounds the LLM in relevant context, a generation step
that produces executable SQL, and a feedback loop that lets the system
recover from its own mistakes — the core pattern behind most modern
retrieval-augmented, tool-using LLM agents.
