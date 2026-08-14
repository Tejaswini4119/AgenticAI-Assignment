"""
Three different multi-step prompt pipelines for summarization, so the same
input document can be run through each and compared:

1. baseline        — one prompt, no chaining. The control group.
2. map_reduce_chain — chunk -> summarize each chunk -> combine into one
                       final summary. Built for documents too long to fit
                       comfortably in a single prompt.
3. refine_chain     — draft -> critique (what's missing?) -> revise. Built
                       to catch facts a first-pass summary drops.
"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm

# Small delay between sequential calls so the multi-call chains (map_reduce,
# refine) don't burst past a free-tier per-minute rate limit.
CALL_DELAY_SECONDS = 1.5

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def baseline(text: str, on_step=None) -> str:
    """Single prompt, no chaining."""
    prompt = (
        "Summarize the following article in 4-6 sentences, capturing the "
        "main argument and the most important concrete facts:\n\n" + text
    )
    summary = llm.generate_text(prompt)
    if on_step:
        on_step("baseline", summary)
    return summary


def map_reduce_chain(text: str, on_step=None) -> str:
    """chunk -> summarize each chunk (map) -> combine (reduce)."""
    chunks = chunk_text(text)
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = (
            "Summarize this excerpt from a longer article in 2-3 sentences. "
            "Preserve concrete facts, numbers, and named entities:\n\n" + chunk
        )
        summary = llm.generate_text(prompt)
        chunk_summaries.append(summary)
        if on_step:
            on_step(f"map[{i + 1}/{len(chunks)}]", summary)
        time.sleep(CALL_DELAY_SECONDS)

    combined = "\n".join(chunk_summaries)
    reduce_prompt = (
        "The following are summaries of consecutive sections of one article, "
        "in order. Combine them into a single coherent 4-6 sentence summary "
        "of the entire article, removing redundancy between sections:\n\n"
        + combined
    )
    final = llm.generate_text(reduce_prompt)
    if on_step:
        on_step("reduce", final)
    return final


def refine_chain(text: str, on_step=None) -> str:
    """draft -> critique (what's missing?) -> revise."""
    draft_prompt = (
        "Write a 4-6 sentence summary of this article:\n\n" + text
    )
    draft = llm.generate_text(draft_prompt)
    if on_step:
        on_step("draft", draft)
    time.sleep(CALL_DELAY_SECONDS)

    critique_prompt = (
        "You are a meticulous editor. Compare the SUMMARY to the ORIGINAL "
        "ARTICLE below. List up to 3 important facts, numbers, or named "
        "entities that appear in the article but are missing from the "
        "summary. If nothing important is missing, respond with exactly: "
        "Nothing missing.\n\n"
        f"ORIGINAL ARTICLE:\n{text}\n\nSUMMARY:\n{draft}"
    )
    critique = llm.generate_text(critique_prompt)
    if on_step:
        on_step("critique", critique)
    time.sleep(CALL_DELAY_SECONDS)

    revise_prompt = (
        "Revise the SUMMARY below to incorporate the MISSING POINTS, while "
        "staying at 4-6 sentences and remaining coherent. If MISSING POINTS "
        "says 'Nothing missing', return the SUMMARY unchanged.\n\n"
        f"SUMMARY:\n{draft}\n\nMISSING POINTS:\n{critique}"
    )
    revised = llm.generate_text(revise_prompt)
    if on_step:
        on_step("revise", revised)
    return revised


STRATEGIES = {
    "baseline": baseline,
    "map_reduce": map_reduce_chain,
    "refine": refine_chain,
}
