"""Retrieval-stage evaluation: does the right passage even reach the model?

Every quality problem found in this project so far has been a retrieval
problem (UNESCO's neural-data provision sat at rank #83 of 228 and never got
into the prompt), but the only metric available was end-to-end answer quality,
which cannot tell a retrieval failure from a generation failure.

This measures the retrieval stage alone:

* **recall** — for each gold passage, did any retrieved chunk contain it?
* **source balance** — how the retrieved chunks split across documents, which
  is where the 19:2 UNESCO/OECD skew shows up.

It is LLM-free and near-instant for single-query modes; multi-query modes still
pay one decomposition call per case (~15s), which is still two orders of
magnitude cheaper than a full end-to-end run.

    python -m evals.retrieval
    python -m evals.retrieval --k 12 --multi-query
"""

import argparse
import re
import time

from evals.dataset import CASES
from rag import retriever
from rag.embeddings import list_sources


def normalise(text: str) -> str:
    """Lowercase and collapse whitespace.

    PDF extraction leaves irregular spacing ("evidence -based", double spaces
    mid-sentence), so raw substring matching against the source text is
    unreliable without this.
    """
    return re.sub(r"\s+", " ", text).strip().lower()


def gold_chunk_found(needle: str, chunks: list[dict]) -> bool:
    """True when any retrieved chunk contains ``needle``."""
    target = normalise(needle)
    return any(target in normalise(chunk["text"]) for chunk in chunks)


def evaluate(k: int, multi_query: bool, label: str) -> dict:
    """Run every gold-chunk case through one retrieval configuration."""
    print(f"\n{'=' * 72}")
    print(f"{label}   (k={k}, multi_query={multi_query})")
    print("=" * 72)

    total_gold = 0
    found_gold = 0
    source_totals: dict[str, int] = {}
    elapsed_total = 0.0

    for case in CASES:
        if not case.gold_chunks:
            continue

        started = time.time()
        chunks, subqueries = retriever.retrieve_for(case.question, k=k, multi_query=multi_query)
        elapsed = time.time() - started
        elapsed_total += elapsed

        for chunk in chunks:
            source_totals[chunk["source"]] = source_totals.get(chunk["source"], 0) + 1

        hits = [gold_chunk_found(g, chunks) for g in case.gold_chunks]
        total_gold += len(hits)
        found_gold += sum(hits)

        status = "ok  " if all(hits) else "MISS"
        print(f"\n[{status}] {case.id}  ({sum(hits)}/{len(hits)} gold, "
              f"{len(chunks)} chunks, {elapsed:.1f}s)")
        for gold, hit in zip(case.gold_chunks, hits):
            print(f"       {'found  ' if hit else 'MISSING'}: {gold[:60]}")
        for subquery in subqueries:
            print(f"       search: {subquery}")

    recall = found_gold / total_gold if total_gold else 0.0
    print(f"\n-- recall: {found_gold}/{total_gold} ({recall:.0%})")
    print(f"-- retrieval time: {elapsed_total:.1f}s total")
    print(f"-- source balance: {source_totals}")
    return {
        "label": label,
        "recall": recall,
        "found": found_gold,
        "total": total_gold,
        "sources": source_totals,
        "seconds": elapsed_total,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, help="override k for a one-off configuration")
    parser.add_argument("--multi-query", action="store_true", help="use sub-query decomposition")
    args = parser.parse_args()

    print("indexed sources:", list_sources())

    if args.k:
        results = [evaluate(args.k, args.multi_query, "custom")]
    else:
        results = [
            evaluate(preset["k"], preset["multi_query"], name)
            for name, preset in retriever.MODES.items()
        ]

    print(f"\n{'=' * 72}\nSUMMARY\n{'=' * 72}")
    print(f"{'configuration':<30}{'recall':>10}{'time':>9}  sources")
    print("-" * 72)
    for r in results:
        balance = ", ".join(f"{s.split('_')[0].split('-')[0]}:{n}" for s, n in sorted(r["sources"].items()))
        print(f"{r['label']:<30}{r['found']:>4}/{r['total']:<5}{r['seconds']:>7.1f}s  {balance}")


if __name__ == "__main__":
    main()
