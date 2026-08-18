"""Gold cases for the Ethics Navigator — the single source of truth for evals.

One dataset serves two consumers with different failure semantics:

* ``evals/`` runs every case against the real corpus (``data/documents/``) and
  reports graded scores.
* ``tests/`` runs the subset that its small fixture corpus can support, as
  binary pass/fail regressions.

``needs_docs``/``absent_docs`` are what make that split safe: a case is only
valid where the documents it depends on are present (and the ones that would
invalidate it are not). Every expected answer below was verified against the
document text before being written down.
"""

from dataclasses import dataclass, field

UNESCO = "UNESCO_397812eng.pdf"
OECD = "OECD-LEGAL-0457-en.pdf"
UDHR = "UN_declaration_HumanRights.pdf"
CAKE = "chocolate-cake-A4.pdf"

MODE_QA = "Question answering"
MODE_BROAD = "Broad principles"


@dataclass(frozen=True)
class Case:
    """One gold question and how to grade the answer to it."""

    id: str
    question: str
    grader: str  # "refusal" | "contains" | "judge"
    expected_mode: str
    # contains: every group must have >=1 hit; entries within a group are
    # alternatives (synonyms/phrasings).
    expect: tuple[tuple[str, ...], ...] = ()
    # Substrings identifying the passages retrieval *should* surface.
    gold_chunks: tuple[str, ...] = ()
    # Documents that must be indexed for the expected answer to be derivable.
    needs_docs: tuple[str, ...] = ()
    # Documents whose presence would invalidate the case (refusal cases).
    absent_docs: tuple[str, ...] = ()
    rubric: tuple[str, ...] = field(default=())


# Principles the corpus actually states. Used as the judge rubric for the
# broad-synthesis case, replacing the keyword coverage metric that produced
# false positives ("safety" anywhere) and false negatives (paraphrase).
PRINCIPLES: tuple[str, ...] = (
    "beneficence / promoting health and well-being",
    "do no harm / avoiding avoidable harm",
    "proportionality of the intervention to its expected benefit",
    "autonomy, freedom of thought, or cognitive liberty",
    "protection of neural data and mental privacy",
    "prior, free and informed consent",
    "non-discrimination, inclusivity, or respect for neurodiversity",
    "accountability and access to remedy for those harmed",
    "transparency and trustworthiness",
    "safety assessment and evidence-based evaluation",
    "equitable access and global justice, including lower-income countries",
    "the best interests of the child and future generations",
    "public and societal deliberation or multi-stakeholder engagement",
    "oversight, regulation, and prohibition of misuse such as social control",
)


CASES: tuple[Case, ...] = (
    Case(
        id="cake-refusal",
        question="Give me a recipe for chocolate cake.",
        grader="refusal",
        expected_mode=MODE_QA,
        absent_docs=(CAKE,),
    ),
    Case(
        id="time-off-right",
        question=(
            "Is the ability to take reasonable time off from work a right, "
            "not a privilege?"
        ),
        grader="contains",
        expected_mode=MODE_QA,
        # UDHR Article 24: "Everyone has the right to rest and leisure,
        # including reasonable limitation of working hours and periodic
        # holidays with pay."
        expect=(
            ("right",),
            ("rest", "leisure", "holiday", "time off"),
        ),
        gold_chunks=("right to rest and leisure",),
        needs_docs=(UDHR,),
    ),
    Case(
        id="oecd-due-regard",
        question=(
            "What societal values does the OECD document say should be shown "
            "due regard?"
        ),
        grader="contains",
        expected_mode=MODE_QA,
        # OECD principle 1(d), verbatim: "...especially privacy, cognitive
        # liberty, and autonomy of individuals."
        expect=(
            ("privacy",),
            ("cognitive liberty",),
            ("autonomy",),
        ),
        gold_chunks=("due regard for human rights and societal values",),
        needs_docs=(OECD,),
    ),
    Case(
        id="cognitive-liberty",
        question="What is cognitive liberty?",
        grader="contains",
        expected_mode=MODE_QA,
        # OECD definitions: "Cognitive liberty: the right to mental
        # self-determination."
        expect=(("mental self-determination", "self-determination", "self determination"),),
        gold_chunks=("Cognitive liberty: the right to mental",),
        needs_docs=(OECD,),
    ),
    Case(
        id="neural-data",
        question="What is neural data?",
        grader="contains",
        expected_mode=MODE_QA,
        # UNESCO §5: "Neural data include qualitative and quantitative data
        # about the structure, activity and function of the nervous system
        # gathered through neurotechnology..."
        expect=(
            ("qualitative", "quantitative"),
            ("structure", "activity", "function"),
            ("nervous system", "brain"),
        ),
        gold_chunks=("Neural data include qualitative and quantitative data",),
        needs_docs=(UNESCO,),
    ),
    Case(
        id="equitable-access",
        question=(
            "How can we ensure that access to evidence-based and reliable "
            "neurotechnology is equitable?"
        ),
        grader="contains",
        expected_mode=MODE_QA,
        # UNESCO §29: "Special attention should be given to LMICs,
        # resource-constrained settings, as well as to the specific needs of
        # different groups..."
        expect=(
            (
                "lmic",
                "low- and middle-income",
                "low and middle income",
                "middle-income",
                "middle income",
            ),
        ),
        gold_chunks=("Equitable access to evidence",),
        needs_docs=(UNESCO,),
    ),
    Case(
        id="broad-principles",
        question=(
            "Please summarize the legal and ethical principles underlying the "
            "responsible development of neurotechnology."
        ),
        grader="judge",
        expected_mode=MODE_BROAD,
        gold_chunks=(
            "Neural data include qualitative and quantitative data",
            "due regard for human rights and societal values",
            "Equitable access to evidence",
        ),
        needs_docs=(UNESCO, OECD),
        rubric=PRINCIPLES,
    ),
)


def cases_for(corpus: set[str], graders: tuple[str, ...] | None = None) -> list[Case]:
    """Return the cases that are valid against ``corpus``.

    A case applies when every document it needs is present and no document
    that would invalidate it is. ``graders`` optionally restricts to specific
    grader types — pytest uses it to skip the judge, which needs a second model.
    """
    selected = []
    for case in CASES:
        if not set(case.needs_docs) <= corpus:
            continue
        if set(case.absent_docs) & corpus:
            continue
        if graders and case.grader not in graders:
            continue
        selected.append(case)
    return selected
