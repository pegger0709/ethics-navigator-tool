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
    """At temperature 0 (+ fixed seed), asking the same question twice is identical."""
    first, second = get_responses(subset, prompt)
    assert first == second


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

    A meaningful answer must commit (not punt with "I don't know"), call it a
    right, and convey that it applies to everyone — capturing the spec's
    "a right for all, not a privilege for some".
    """
    response, _ = get_responses((D1,), P1)
    lowered = response.lower()
    assert not is_refusal(response), f"Expected a committed answer, got: {response}"
    assert "right" in lowered, f"Expected the answer to call it a right, got: {response}"
    assert any(word in lowered for word in ("everyone", "all", "universal")), (
        f"Expected the answer to convey it applies to everyone, got: {response}"
    )


def test_d2_answers_cake_question(get_responses):
    """The recipe says to bake 30-35 minutes, until a toothpick comes out clean."""
    response, _ = get_responses((D2,), P2)
    lowered = response.lower()
    assert not is_refusal(response), f"Expected a grounded answer, got: {response}"
    assert "30" in response and ("35" in response or "toothpick" in lowered), (
        f"Expected the 30-35 minute / toothpick instruction, got: {response}"
    )
