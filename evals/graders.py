"""Graders for eval cases: refusal, keyword containment, and LLM-as-judge.

Kept separate from the runners so ``tests/`` and ``evals/`` grade identically —
a regression test and an eval score should never disagree about what "correct"
means for the same case. (``tests/`` currently keeps its own, independent
phrase-based refusal check for speed and to avoid a judge-model dependency in
the fast regression suite; the two are not yet unified.)
"""

from evals.textnorm import normalize
from llm import ollama_client

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

# A phrase list kept missing real refusals: three different models each
# declined in a phrasing that wasn't on it ("I don't have the ingredients or
# instructions...", "I cannot provide... based on the provided context").
# Asking a model "does this decline to answer" is the same kind of task as
# JUDGE_PROMPT — robust to phrasing in a way no phrase list can be — so
# refusal detection uses the same mechanism instead of a growing list.
JUDGE_REFUSAL_PROMPT = (
    "You are grading whether an answer declines to answer a question — for "
    "example by saying it does not have enough information, that the "
    "relevant document was not provided or indexed, or that it does not "
    "know.\n\n"
    "ANSWER:\n{answer}\n\n"
    "Does the answer decline to answer? Reply with exactly one word: YES or NO."
)


def grade_refusal(response: str, model: str | None = None) -> bool:
    """Ask the judge model whether ``response`` declines to answer.

    One call, temperature 0. A failed judge call counts as "not a refusal"
    rather than crashing the eval — the conservative side, since it means the
    case does not get credited on an indeterminate result.
    """
    model = model or ollama_client.JUDGE_MODEL
    messages = [{"role": "user", "content": JUDGE_REFUSAL_PROMPT.format(answer=response)}]
    try:
        raw = ollama_client.chat(messages, stream=False, model=model) or ""
    except Exception:  # noqa: BLE001 — an indeterminate judgement is not a refusal
        return False
    return raw.strip().upper().startswith("YES")


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
