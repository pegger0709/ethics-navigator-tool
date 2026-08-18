"""Integration tests for the RAG pipeline: determinism, grounding, no hallucination."""

import pytest

from tests.conftest import D1, D2, P1, P2, SUBSETS, subset_id

REFUSAL_PHRASES = [
    "don't know",
    "do not know",
    "doesn't contain",
    "does not contain",
    "no information",
    "not mentioned",
    "doesn't mention",
    "does not mention",
    "no relevant context",
    "unable to find",
    "can't find",
    "cannot find",
]


def is_refusal(response: str) -> bool:
    lowered = response.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


@pytest.mark.parametrize("subset", SUBSETS, ids=subset_id)
@pytest.mark.parametrize("prompt", [P1, P2], ids=["P1", "P2"])
def test_determinism(get_responses, subset, prompt):
    """At temperature 0, the model makes the same answer-vs-refuse decision each run.

    Bit-identical tokens are not achievable on this stack: llama.cpp's multithreaded
    matrix reductions are floating-point non-associative, so near-tie logits can flip
    between runs regardless of seed. What temperature=0 actually guarantees is
    behavioral consistency — the model always commits or always refuses for the same
    (subset, prompt) pair. The content tests verify answer quality separately.
    """
    first, second = get_responses(subset, prompt)
    assert is_refusal(first) == is_refusal(second), (
        f"Inconsistent answer-vs-refuse decision across two runs:\n"
        f"First:  {first}\nSecond: {second}"
    )


def test_d1_does_not_answer_cake_question(get_responses):
    """The human-rights document contains nothing about baking: expect a refusal."""
    response, _ = get_responses((D1,), P2)
    assert is_refusal(response), f"Expected an 'I don't know' answer, got: {response}"


def test_d2_does_not_answer_rights_question(get_responses):
    """The cake recipe contains nothing about labor rights: expect a refusal."""
    response, _ = get_responses((D2,), P1)
    assert is_refusal(response), f"Expected an 'I don't know' answer, got: {response}"


def test_d1_answers_rights_question(get_responses):
    """Article 24 grants rest and leisure to *everyone* — a right for all, not a privilege.

    A meaningful answer must:
    - commit (not punt with 'I don't know')
    - cite the specific right from Article 24 ('right to rest' or 'right to leisure')
    - convey universality ('everyone', 'all', 'universal')
    - not call it a privilege (or if 'privilege' appears, it must be negated)
    """
    response, _ = get_responses((D1,), P1)
    lowered = response.lower()
    assert not is_refusal(response), f"Expected a committed answer, got: {response}"
    assert "right to rest" in lowered or "right to leisure" in lowered, (
        f"Expected Article 24's specific right (rest/leisure) in the answer, got: {response}"
    )
    assert any(word in lowered for word in ("everyone", "all", "universal")), (
        f"Expected the answer to convey universality, got: {response}"
    )
    # If "privilege" appears at all it must be rejected, not endorsed — but
    # accept the various ways that rejection gets phrased.
    privilege_rejected = any(
        phrase in lowered
        for phrase in (
            "not a privilege",
            "rather than a privilege",
            "instead of a privilege",
            "not merely a privilege",
            "not just a privilege",
        )
    )
    assert "privilege" not in lowered or privilege_rejected, (
        f"Expected the answer to reject the 'privilege' framing, got: {response}"
    )


def test_d2_answers_cake_question(get_responses):
    """The recipe says to bake 30-35 minutes, until a toothpick comes out clean."""
    response, _ = get_responses((D2,), P2)
    lowered = response.lower()
    assert not is_refusal(response), f"Expected a grounded answer, got: {response}"
    assert "30" in response and ("35" in response or "toothpick" in lowered), (
        f"Expected the 30-35 minute / toothpick instruction, got: {response}"
    )
