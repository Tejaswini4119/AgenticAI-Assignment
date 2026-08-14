# Experiment 3 — Prompt Chaining for Summarization

Experiment with multiple **multi-step prompt pipelines** for the same task
(summarization) and compare how the pipeline structure changes the result,
rather than just chaining prompts once and moving on.

## The three pipelines (`chains.py`)

| Strategy | Steps | Built for |
|---|---|---|
| `baseline` | 1 prompt: summarize the whole document | Control group — no chaining at all |
| `map_reduce` | chunk → summarize each chunk (map) → combine into one summary (reduce) | Documents too long to summarize in one prompt |
| `refine` | draft → critique ("what's missing?") → revise | Catching facts a first-pass summary drops |

All three run through the same `common/llm.py` helper as the other
experiments, and `main.py` runs all three on the same document back-to-back
so you can see exactly where each pipeline's intermediate outputs diverge.

## Sample document

`documents/container_shipping.txt` — a ~630-word, self-authored article on
the history of container shipping, deliberately packed with concrete facts
and numbers (dates, costs, named ships and people) so it's easy to spot
which pipeline preserves them and which loses them in a summary.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 03_prompt_chaining/main.py
```

Press Enter at the file prompt to use the bundled sample article, or type a
path to your own `.txt` file. Needs `GEMINI_API_KEY` in the repo-root
`.env`; without one, calls fall back to an offline mock.

## What to look for

- Does `map_reduce`'s final summary read as coherent, or does it feel like
  three summaries glued together? That's the "reduce" prompt's job to fix.
- Does `refine`'s critique step actually catch something real, or does it
  just say "Nothing missing" every time? Try it on an article with more
  numbers/names if the critique step feels too easy to satisfy.
- `map_reduce` makes `len(chunks) + 1` LLM calls, `refine` makes 3,
  `baseline` makes 1 — chaining is not free, and the CLI prints every
  intermediate step so the cost is visible, not hidden.

## Files

| File | Purpose |
|---|---|
| `documents/container_shipping.txt` | Sample source article |
| `chains.py` | The three pipeline implementations |
| `main.py` | CLI: runs all three strategies, prints every intermediate step, then a final side-by-side |

## Notes / limitations

- `chains.py` adds a 1.5s delay between sequential calls inside
  `map_reduce`/`refine` to avoid bursting past a free-tier per-minute rate
  limit — with 7-8 chained calls per run across all three strategies, this
  is easy to hit. If it still trips mid-run, remaining steps fall back to
  the offline mock (visible as `[offline-mock reply to: ...]`) rather than
  crashing — that's the same graceful-degradation behavior as experiments
  1 and 2, not a bug.
- The critique step in `refine_chain` is only as good as the LLM's ability
  to actually compare two texts; it can occasionally miss things or flag
  something already present.
