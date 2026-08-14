"""
Experiment 3: Prompt Chaining for Summarization

Runs the same source document through three different multi-step prompt
pipelines (see chains.py) and prints every intermediate step, so you can
see where each pipeline diverges and compare the final summaries.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chains import STRATEGIES

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOC = os.path.join(HERE, "documents", "container_shipping.txt")


def load_document(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_strategy(name: str, fn, text: str):
    print("\n" + "=" * 70)
    print(f"  Strategy: {name}")
    print("=" * 70)

    def on_step(label, output):
        print(f"\n--- [{name}] {label} " + "-" * max(1, 50 - len(label)))
        print(output.strip())

    final = fn(text, on_step=on_step)
    return final


def main():
    print("=" * 70)
    print("  Experiment 3: Prompt Chaining for Summarization")
    print("=" * 70)

    path = input(
        f"\nPath to a .txt file to summarize [default: {os.path.basename(DEFAULT_DOC)}]: "
    ).strip()
    path = path or DEFAULT_DOC
    text = load_document(path)
    print(f"\nLoaded '{os.path.basename(path)}' ({len(text.split())} words).")

    results = {}
    for name, fn in STRATEGIES.items():
        results[name] = run_strategy(name, fn, text)

    print("\n" + "=" * 70)
    print("  FINAL SUMMARIES SIDE BY SIDE")
    print("=" * 70)
    for name, summary in results.items():
        print(f"\n[{name}] ({len(summary.split())} words)")
        print(summary.strip())

    print(f"\nOriginal document: {len(text.split())} words.")
    print("\nDone. Notice how 'refine' can add back facts 'baseline' drops,")
    print("and how 'map_reduce' handles length by never seeing the whole")
    print("document in one prompt.")


if __name__ == "__main__":
    main()
