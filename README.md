# Laboratory Experiments (Case Study–Driven)

Twelve hands-on labs covering the LLM/agentic-AI stack end to end — from a
single prompt call up to a capstone system. Each experiment is a
self-contained folder with its own `README.md` and `main.py` you can run
directly. They share one LLM helper (`common/llm.py`, Gemini-backed with an
offline mock fallback) so the pattern stays consistent across labs.

## Setup

```bash
cd experiments
pip install -r requirements.txt      # or reuse the venv from assignment-agenticai/
```

Requires `GEMINI_API_KEY` in `experiments/.env` (copy `experiments/.env.template`
— `common/llm.py` also checks the repo root and `assignment-agenticai/.env`
as fallbacks). Every lab still runs without a key — LLM calls fall back to
a deterministic offline mock so the pipeline logic is visible even without
API access.

**Free-tier quota heads-up:** Gemini's free tier currently caps
`gemini-2.5-flash` at **20 requests/day**. Chained/agentic labs (3, 4, and
especially 5+) can burn through that in one or two runs — if you see
`[offline-mock reply to: ...]` output mid-run, that's the fallback kicking
in, not a bug.

## Status

| # | Experiment | Folder | Status |
|---|---|---|---|
| 1 | Text-to-SQL Workflow | [`01_text_to_sql`](01_text_to_sql) | ✅ Done |
| 2 | RAG-Based Question Answering | [`02_rag_qa`](02_rag_qa) | ✅ Done |
| 3 | Prompt Chaining for Summarization | [`03_prompt_chaining`](03_prompt_chaining) | ✅ Done |
| 4 | SQL Agent with Tool Use | [`04_sql_agent`](04_sql_agent) | ✅ Done |
| 5 | Multi-Agent SDR System | [`05_multi_agent_sdr`](05_multi_agent_sdr) | ✅ Done |
| 6 | Policy Compliance Agent | [`06_policy_compliance_agent`](06_policy_compliance_agent) | ✅ Done |
| 7 | Deep Research Agent Workflow | [`07_deep_research_agent`](07_deep_research_agent) | ✅ Done |
| 8 | Image Retrieval / Visual QA | [`08_visual_qa`](08_visual_qa) | ✅ Done |
| 9 | Reasoning Model Benchmarking | [`09_reasoning_benchmark`](09_reasoning_benchmark) | ✅ Done |
| 10 | Fine-Tuning for Domain Adaptation | `10_fine_tuning` | ⏳ Planned |
| 11 | Model Optimization Experiment | `11_model_optimization` | ⏳ Planned |
| 12 | Mini Project (Capstone) | `12_capstone` | ⏳ Planned |

## What each one covers

1. **Text-to-SQL Workflow** — embed table schemas, retrieve the relevant
   ones for a question, generate SQL, execute it, self-repair on error,
   answer in natural language.
2. **RAG-Based QA** — chunk/index documents, retrieve top-k chunks,
   generate a grounded answer.
3. **Prompt Chaining for Summarization** — multi-step pipeline (summarize →
   extract → refine) instead of one monolithic prompt.
4. **SQL Agent with Tool Use** — a ReAct loop that chooses between
   schema-lookup, query, and validation tools rather than a fixed pipeline.
5. **Multi-Agent SDR System** — separate lead-gen, qualification, and
   outreach agents handing off structured state to each other.
6. **Policy Compliance Agent** — evaluates synthetic records against a
   rule set and explains violations.
7. **Deep Research Agent Workflow** — plans sub-questions, researches each,
   reflects, and drafts a final report.
8. **Image Retrieval / Visual QA** — multimodal embedding search over
   images plus question answering about a selected image.
9. **Reasoning Model Benchmarking** — same problem set run under different
   prompting strategies (direct, CoT, self-consistency), scored side by side.
10. **Fine-Tuning for Domain Adaptation** — LoRA fine-tune of a small open
    model on a narrow domain, evaluated before/after.
11. **Model Optimization** — quantize (or distill) a model and compare
    size/latency/quality trade-offs against the baseline.
12. **Mini Project (Capstone)** — combines retrieval, tools, and multiple
    agents from labs 1–11 into one deployed system.

Labs are built one at a time, fully working, in this order — see the status
table above for what's done.
