"""Measure whether each answer mode delivers what it promises.

This is an *evaluation* harness, not a test suite. The pytest suite checks
pipeline plumbing quickly against a small model; this runs the real corpus
through the real model and scores answer quality, so it is slow (tens of
minutes) and meant to be run deliberately.

It answers three questions:

* **Coverage** — for a broad question, how many of the principles the source
  documents actually state make it into the answer? This is the metric that
  exposed retrieval burying UNESCO's neural-data provision.
* **Latency** — does each mode's speed match what its description implies?
* **Grounding** — are off-corpus questions still refused, and are both source
  documents cited when both are relevant?

Run as a module from the repo root so ``rag``/``llm`` are importable::

    python -m evals.evaluate_modes
    python -m evals.evaluate_modes --model qwen2.5:7b
    python -m evals.evaluate_modes --mode "Broad synthesis"
"""

import argparse
import time

from llm import ollama_client
from rag import retriever

BROAD_QUERY = (
    "Please summarize the legal and ethical principles underlying the "
    "responsible development of neurotechnology."
)
NARROW_QUERY = "What is the definition of personal brain data?"
OFF_CORPUS_QUERY = "How long should I bake a chocolate cake?"

# Principles the source documents actually state, each with the alternative
# wordings that count as covering it. Derived by reading the documents, so a
# miss here is a genuine gap in the answer rather than a phrasing quirk.
EXPECTED_TOPICS: dict[str, tuple[str, ...]] = {
    "beneficence / do no harm": ("do no harm", "beneficence", "avoidable harm"),
    "proportionality": ("proportional", "proportionality"),
    "autonomy / freedom of thought": ("autonomy", "freedom of thought", "self-determination"),
    "neural data & mental privacy": ("neural data", "brain data", "mental privacy"),
    "informed consent": ("informed consent", "free and informed"),
    "non-discrimination": ("discriminat", "neurodiversity"),
    "accountability": ("accountab",),
    "transparency / trustworthiness": ("transparen", "trustworth"),
    "safety assessment": ("safety",),
    "equitable access / global justice": ("equitable", "equity", "lmic", "global justice"),
    "children / future generations": ("child", "future generations"),
    "societal deliberation": ("deliberation", "public dialogue", "stakeholder", "engagement"),
    "oversight & regulation": ("oversight", "regulat"),
    "misuse / social control": ("misuse", "social control", "manipulat", "surveillance"),
}

REFUSAL_PHRASES = (
    "don't know",
    "do not know",
    "does not contain",
    "doesn't contain",
    "no information",
    "not mentioned",
    "no relevant context",
)

SOURCES = ("UNESCO_397812eng.pdf", "OECD-LEGAL-0457-en.pdf")


def is_refusal(response: str) -> bool:
    lowered = response.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def covered_topics(response: str) -> list[str]:
    """Return the expected topics that appear in ``response``."""
    lowered = response.lower()
    return [
        topic
        for topic, keywords in EXPECTED_TOPICS.items()
        if any(keyword in lowered for keyword in keywords)
    ]


def run_case(query: str, k: int, multi_query: bool) -> dict:
    """Answer one query and collect timing plus the retrieved sources."""
    started = time.time()
    stream, chunks, meta = retriever.answer(query, k=k, multi_query=multi_query)
    response = "".join(stream)
    elapsed = time.time() - started

    source_counts: dict[str, int] = {}
    for chunk in chunks:
        source_counts[chunk["source"]] = source_counts.get(chunk["source"], 0) + 1

    return {
        "response": response,
        "seconds": elapsed,
        "chunks": len(chunks),
        "sources": source_counts,
        "subqueries": meta["subqueries"],
    }


def evaluate_mode(name: str, preset: dict) -> dict:
    """Run every case against one mode and score it."""
    k, multi_query = preset["k"], preset["multi_query"]
    print(f"\n{'=' * 70}\nMODE: {name}  (k={k}, multi_query={multi_query})\n{'=' * 70}")

    broad = run_case(BROAD_QUERY, k, multi_query)
    covered = covered_topics(broad["response"])
    missing = [t for t in EXPECTED_TOPICS if t not in covered]
    cited = [s for s in SOURCES if s.split("-")[0].split("_")[0].lower() in broad["response"].lower()]

    print(f"\n-- broad question ({broad['seconds']:.0f}s, {broad['chunks']} chunks)")
    if broad["subqueries"]:
        for subquery in broad["subqueries"]:
            print(f"   search: {subquery}")
    print(f"   coverage: {len(covered)}/{len(EXPECTED_TOPICS)} topics")
    print(f"   missing : {', '.join(missing) if missing else '(none)'}")
    print(f"   sources retrieved: {broad['sources']}")
    print(f"   sources cited    : {cited or '(none)'}")

    narrow = run_case(NARROW_QUERY, k, multi_query)
    narrow_ok = not is_refusal(narrow["response"]) and "brain" in narrow["response"].lower()
    print(f"\n-- narrow question ({narrow['seconds']:.0f}s): "
          f"{'answered' if narrow_ok else 'FAILED to answer'}")

    off = run_case(OFF_CORPUS_QUERY, k, multi_query)
    off_ok = is_refusal(off["response"])
    print(f"-- off-corpus question ({off['seconds']:.0f}s): "
          f"{'refused (correct)' if off_ok else 'ANSWERED (hallucination risk)'}")

    return {
        "mode": name,
        "coverage": len(covered),
        "missing": missing,
        "broad_seconds": broad["seconds"],
        "narrow_ok": narrow_ok,
        "off_corpus_ok": off_ok,
        "total_seconds": broad["seconds"] + narrow["seconds"] + off["seconds"],
        "sources_cited": len(cited),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="override CHAT_MODEL for this run")
    parser.add_argument("--mode", action="append", help="only run this mode (repeatable)")
    args = parser.parse_args()

    if args.model:
        ollama_client.CHAT_MODEL = args.model
    ollama_client.ensure_models()

    modes = {m: retriever.MODES[m] for m in args.mode} if args.mode else retriever.MODES
    print(f"model: {ollama_client.CHAT_MODEL}")

    results = [evaluate_mode(name, preset) for name, preset in modes.items()]

    print(f"\n{'=' * 70}\nSUMMARY ({ollama_client.CHAT_MODEL})\n{'=' * 70}")
    header = f"{'mode':<28}{'coverage':>10}{'cites':>7}{'broad':>9}{'narrow':>8}{'refuses':>9}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['mode']:<28}"
            f"{r['coverage']:>7}/{len(EXPECTED_TOPICS):<2}"
            f"{r['sources_cited']:>6}/2"
            f"{r['broad_seconds']:>8.0f}s"
            f"{'  ok' if r['narrow_ok'] else '  FAIL':>8}"
            f"{'  ok' if r['off_corpus_ok'] else '  FAIL':>9}"
        )


if __name__ == "__main__":
    main()
