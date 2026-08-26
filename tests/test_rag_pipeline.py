"""Integration tests for the RAG pipeline: determinism, grounding, no hallucination."""

import re

import pytest

from tests.conftest import D1, D2, P1, P2, SUBSETS, subset_id

# Models phrase refusals in far more ways than a list of literal substrings can
# track. This suite was broken once by "does not provide information", which no
# literal covered even though four near-identical ones were listed — so match
# the *shape* of a refusal instead of its exact wording.
#
# Two shapes cover what this pipeline actually produces. Both are anchored
# deliberately: an unanchored "does not <verb>" would also fire on a genuine
# answer that happens to carry a caveat ("Article 24 does not define leisure
# precisely, but everyone has the right to rest"), which must NOT read as a
# refusal — the answer-quality tests below assert exactly that.
#
# evals/graders.py solves this same problem with an LLM judge. That is
# deliberately not reused here: pytest is the fast regression gate and must not
# depend on a second model being pulled.
_SOURCE = r"(?:context|document|text|excerpt|passage|recipe|source|information)s?"
_NEGATION = r"(?:does not|doesn't|do not|don't|did not|didn't|cannot|can't|is not|isn't)"
_TELLING = (
    r"(?:contain|mention|provide|include|specify|state|discuss|detail|address"
    r"|cover|define|describe|have|know|find|say)"
)
REFUSAL_PATTERN = re.compile(
    # "The context does not contain / provide information about ..."
    rf"\b{_SOURCE}\b[\w\s,'\"-]{{0,40}}?\b{_NEGATION}\b[\w\s,]{{0,40}}?\b{_TELLING}\b"
    # "I cannot provide ...", "I don't have that information"
    rf"|\b(?:i|we)\b\s+(?:{_NEGATION}|am unable to|are unable to)\s"
    rf"[\w\s,]{{0,30}}?\b{_TELLING}\b"
)

# Stock refusals that do not fit either shape above.
REFUSAL_PHRASES = (
    "no relevant context",
    "no information",
    "insufficient information",
    "not mentioned",
    "unable to find",
)


def is_refusal(response: str) -> bool:
    lowered = response.lower()
    if REFUSAL_PATTERN.search(lowered):
        return True
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
