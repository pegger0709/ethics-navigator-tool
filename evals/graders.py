"""Graders for eval cases: refusal, keyword containment, and LLM-as-judge.

Kept separate from the runners so ``tests/`` and ``evals/`` grade identically —
a regression test and an eval score should never disagree about what "correct"
means for the same case.
"""

from evals.textnorm import normalize
from llm import ollama_client

REFUSAL_PHRASES = (
    "don't know",
    "do not know",
    "doesn't contain",
    "does not contain",
    "no information",
    "don't have that information",
    "don't have any information",
    "don't have information",
    "not mentioned",
    "doesn't mention",
    "does not mention",
    "no relevant context",
    "unable to find",
    "can't find",
    "cannot find",
    "not able to provide",
    "no relevant",
)

# Deliberately narrow: the judge answers one yes/no question about one
# principle at a time. Asking a 12B model "is this a good summary?" invites
# vague agreement; asking whether a specific claim is present is a much easier
# task that a small model can do reliably.
JUDGE_PROMPT = (
    "You are grading whether an answer mentions a specific principle.\n\n"
    "PRINCIPLE: {item}\n\n"
    "ANSWER:\n{answer}\n\n"
    "Does the answer state or clearly convey that principle? It does not need "
    "to use the same words. Reply with exactly one word: YES or NO."
)


def grade_refusal(response: str) -> bool:
    """True when the response declines to answer."""
    normalized = normalize(response)
    return any(phrase in normalized for phrase in REFUSAL_PHRASES)


def grade_contains(
    response: str, expect: tuple[tuple[str, ...], ...]
) -> tuple[bool, list[tuple[str, ...]]]:
    """Check every required group has at least one of its alternatives present.

    Returns ``(passed, missing_groups)`` so a failure says which expectation
    was unmet rather than just that something was. Both sides are normalized,
    so a model writing "self‑determination" with a non-breaking hyphen still
    matches a gold phrase written with a plain ASCII one.
    """
    normalized = normalize(response)
    missing = [
        group
        for group in expect
        if not any(normalize(alternative) in normalized for alternative in group)
    ]
    return not missing, missing


def grade_judge(
    response: str, rubric: tuple[str, ...], model: str | None = None
) -> dict[str, bool]:
    """Ask the judge model, per rubric item, whether the answer conveys it.

    One call per item at temperature 0. Any answer that isn't recognisably YES
    counts as NO, so a confused judge under-credits rather than inflating the
    score.
    """
    model = model or ollama_client.JUDGE_MODEL
    verdicts: dict[str, bool] = {}
    for item in rubric:
        messages = [
            {"role": "user", "content": JUDGE_PROMPT.format(item=item, answer=response)}
        ]
        try:
            raw = ollama_client.chat(messages, stream=False, model=model) or ""
        except Exception:  # noqa: BLE001 — a failed judgement is a "no", not a crash
            raw = ""
        verdicts[item] = raw.strip().upper().startswith("YES")
    return verdicts
