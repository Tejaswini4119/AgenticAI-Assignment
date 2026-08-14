# Experiment 2 — RAG-Based Question Answering System

Implement **indexing**, **retrieval**, and **response generation** over a
small multi-document knowledge base, with answers grounded in — and cited
to — the retrieved source text.

## Pipeline

```
documents/*.txt
   │
   ▼
1. Indexing (indexer.py)   — chunk each document (600 chars, 120 overlap),
                              embed every chunk, cache to rag_index.json
                              (auto-rebuilds if documents/ changes)
   │
question ─┐
          ▼
2. Retrieval (retriever.py) — embed the question, rank ALL chunks across
                               ALL documents by cosine similarity, keep top-k
          │
          ▼
3. Generation (main.py)     — LLM answers using only the retrieved chunks,
                               citing which document each fact came from;
                               told explicitly to say "not enough info"
                               rather than guess
```

## Knowledge base

Three short, self-authored documents so retrieval actually has to
discriminate between topics:

- `documents/product_faq.txt` — a fictitious cloud storage product's FAQ
  (pricing, refunds, upload limits, support).
- `documents/employee_handbook.txt` — PTO, remote work, expenses, leave
  policy excerpts.
- `documents/onboarding_guide.txt` — new-hire setup, equipment, benefits
  enrollment.

A question about refunds should only pull from `product_faq.txt`; a
question about sick leave should only pull from `employee_handbook.txt` —
even though all three are indexed together.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # or reuse an existing venv with these deps
python 02_rag_qa/main.py
```

Needs `GEMINI_API_KEY` in the repo-root `.env`. Without one, calls fall back
to an offline mock so the pipeline still runs end to end.

Try:
- `what's the refund policy for Nimbus?`
- `how much PTO do I accrue per month?`
- `what equipment do new hires get?`
- `reindex` — force a rebuild of the embedding index
- `exit` — quit

## Files

| File | Purpose |
|---|---|
| `documents/` | Sample multi-document knowledge base |
| `indexer.py` | Text extraction (.txt, optionally .pdf via `pypdf`), chunking, embedding, caching |
| `retriever.py` | Embeds the query, ranks all indexed chunks by cosine similarity |
| `main.py` | CLI: retrieval → grounded, cited answer generation |

## Notes / limitations

- Retrieval ranks chunks globally, not per-document — a document that's
  verbose or has more overlapping chunks has more chances to show up,
  which is a real bias in naive top-k RAG.
- The `[sources]` list is printed with raw similarity scores so you can see
  when the top hit is a weak match (flagged `low relevance` below 0.55) —
  a real system would use this to decide whether to answer at all.
- Chunking is fixed-size with overlap, not sentence/semantic-aware, so a
  fact can occasionally be split across two chunks.
