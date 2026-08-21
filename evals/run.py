"""Full answer-quality scorecard: the real corpus, the real model, graded.

This is the *only* place gold questions, expected answers, and grading logic
are defined for end-to-end evaluation — evals/dataset.py holds the cases,
evals/graders.py holds the grading, this file only orchestrates and reports.
Anything that isn't in dataset.py isn't an official yardstick, it's opinion.

Slow and deliberate by design: it calls the real chat model once per case
(twice for the judge case, which also makes one judge call per rubric item).
For a fast, LLM-free check of the retrieval stage alone, use
``python -m evals.retrieval`` instead.

    python -m evals.run
    python -m evals.run --model llama3.1:8b
    python -m evals.run --case broad-principles
"""

import argparse
import os
import time

from evals.dataset import cases_for
from evals.graders import grade_contains, grade_judge, grade_refusal
from llm import ollama_client
from rag import retriever
from rag.embeddings import DOCUMENTS_DIR


def current_corpus() -> set[str]:
    """Source filenames actually on disk, so cases can be selected offline."""
    if not os.path.isdir(DOCUMENTS_DIR):
        return set()
    return {
        name
        for name in os.listdir(DOCUMENTS_DIR)
        if os.path.isfile(os.path.join(DOCUMENTS_DIR, name)) and name != ".gitkeep"
    }


def run_case(case) -> dict:
    """Answer one gold question through the real pipeline and grade it."""
    started = time.time()
    stream, chunks, meta = retriever.answer(case.question, mode=case.expected_mode)
    response = "".join(stream)
    elapsed = time.time() - started

    result = {
        "id": case.id,
        "grader": case.grader,
        "mode_used": meta["mode"],
        "seconds": elapsed,
        "chunks": len(chunks),
        "response": response,
    }

    if case.grader == "refusal":
        result["passed"] = grade_refusal(response)
    elif case.grader == "contains":
        passed, missing = grade_contains(response, case.expect)
        result["passed"] = passed
        result["missing"] = missing
    elif case.grader == "judge":
        verdicts = grade_judge(response, case.rubric)
        result["verdicts"] = verdicts
        result["coverage"] = sum(verdicts.values())
        result["rubric_size"] = len(case.rubric)
        result["passed"] = result["coverage"] == result["rubric_size"]
    else:
        raise ValueError(f"unknown grader: {case.grader!r}")

    return result


def print_result(case, result: dict) -> None:
    status = "PASS" if result["passed"] else "FAIL"
    mode_note = "" if result["mode_used"] == case.expected_mode else (
        f"  [!] routed to {result['mode_used']!r}, expected {case.expected_mode!r}"
    )
    print(f"\n[{status}] {case.id} ({result['seconds']:.0f}s, {result['chunks']} chunks){mode_note}")
    print(f"    Q: {case.question}")

    if case.grader == "contains" and result.get("missing"):
        print(f"    missing: {result['missing']}")
    if case.grader == "judge":
        print(f"    coverage: {result['coverage']}/{result['rubric_size']}")
        for item, ok in result["verdicts"].items():
            if not ok:
                print(f"      no: {item}")

    preview = result["response"][:200].replace("\n", " ")
    print(f"    A: {preview}{'...' if len(result['response']) > 200 else ''}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="override CHAT_MODEL for this run")
    parser.add_argument("--case", action="append", help="only run this case id (repeatable)")
    args = parser.parse_args()

    if args.model:
        ollama_client.CHAT_MODEL = args.model
    ollama_client.ensure_models()

    cases = cases_for(current_corpus())
    if args.case:
        cases = [c for c in cases if c.id in args.case]
        missing = set(args.case) - {c.id for c in cases}
        if missing:
            print(f"unknown or inapplicable case id(s): {sorted(missing)}")

    print(f"model: {ollama_client.CHAT_MODEL}")
    print(f"running {len(cases)} of {len(cases_for(current_corpus()))} applicable cases")

    results = []
    for case in cases:
        result = run_case(case)
        print_result(case, result)
        results.append((case, result))

    print(f"\n{'=' * 70}\nSUMMARY ({ollama_client.CHAT_MODEL})\n{'=' * 70}")
    passed = sum(1 for _, r in results if r["passed"])
    for case, r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        extra = f"  {r['coverage']}/{r['rubric_size']}" if case.grader == "judge" else ""
        print(f"  {mark}  {case.id:<24} {r['seconds']:>6.0f}s{extra}")
    print(f"\n{passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
