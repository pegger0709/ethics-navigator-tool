"""Derive the externally shareable report from the internal one.

Run: python report/make_public.py

Written as a script rather than a hand-edited copy so that the two reports
cannot drift: every change to the internal report can be re-projected, and the
exact set of redactions stays reviewable in one place.

What is removed: the company, the named workshop and its location, the named
partner organisation, the citation to the internal workshop report, and every
verbatim participant quote (paraphrased into indirect, unattributed description
of the same feedback theme).

What is deliberately NOT touched: system architecture, model choices, evaluation
methodology, gold dataset design, every number, every table, the trade-off
analysis, the rejected approaches, and all engineering findings. The public
legal and ethical source documents stay named, since they are public.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "ethics-navigator-report.qmd"
DST = HERE / "ethics-navigator-report-public.qmd"

# (old, new) applied in order. Every one must match exactly once, or the script
# fails loudly rather than silently shipping an un-redacted report.
REPLACEMENTS: list[tuple[str, str]] = [
    # --- front matter -------------------------------------------------------
    (
        'subtitle: "Design, architecture, and evaluation of the conversational '
        'successor to the rules-based Navigation Tool"',
        'subtitle: "Design, architecture, and evaluation of a conversational '
        'successor to a rules-based assessment tool"',
    ),
    ("bibliography: references.bib", "bibliography: references-public.bib"),

    # --- PDF layout ---------------------------------------------------------
    # The architecture diagram is ~3:1, far wider than a portrait text block,
    # and Quarto scales it to the page *height* — which left it drawn 2242pt
    # wide on a 612pt page, running off the edge. pdflscape gives it its own
    # rotated page; the explicit fig-width below is what actually sizes it.
    (
        """  pdf:
    toc: true
    number-sections: true
execute:""",
        """  pdf:
    toc: true
    number-sections: true
    include-in-header:
      text: |
        \\usepackage{pdflscape}
execute:""",
    ),

    # --- overview -----------------------------------------------------------
    (
        """It is the successor to a rules-based Navigation Tool piloted at the Asilomar
workshop in March 2026 [@asilomar2026workshop]. That earlier tool asked a fixed
questionnaire and returned red flags. Workshop participants rejected it for
rigidity: the questions felt "too academic, obvious, or leading", the scope was
"too narrowly focused on partnerships", and it "doesn't feel like it fits into a
real workflow". The most frequently requested replacement was, in participants'
own words, an "interactive 'chatbot' type portal" and an "AI-Agent as process
facilitator". This system is that pivot: from a fixed decision tree to a
grounded conversation over primary sources.""",
        """It is the successor to a rules-based assessment tool piloted at an external
practitioner workshop in early 2026. That earlier tool asked a fixed
questionnaire and returned red flags. Practitioners who tested it rejected it as
too rigid: they found the questions academic and leading, the scope confined too
narrowly to partnership review, and the whole exercise a poor fit for how they
actually work. The most frequently requested replacement was a conversational
interface — an assistant that could facilitate the process rather than
administer a form. This system is that pivot: from a fixed decision tree to a
grounded conversation over primary sources.""",
    ),

    # --- problem statement --------------------------------------------------
    (
        """A neurotechnology company faces a proliferation of ethical and regulatory
guidance with, as the workshop framing put it, "unclear implementation
pathways". The instruments are public, lengthy, and written for regulators""",
        """A neurotechnology company faces a proliferation of ethical and regulatory
guidance whose implementation pathways are, as practitioners put it, unclear.
The instruments are public, lengthy, and written for regulators""",
    ),
    (
        """today requires either in-house neuroethics expertise — which the workshop
identified as absent in most companies — or expensive external counsel.""",
        """today requires either in-house neuroethics expertise — which practitioner
feedback identified as absent in most companies — or expensive external counsel.""",
    ),

    # --- motivation ---------------------------------------------------------
    (
        """The motivation is documented rather than assumed. The predecessor tool was
tested by practitioners at the Asilomar workshop, and its shortcomings were
recorded in structured feedback [@asilomar2026workshop].""",
        """The motivation is documented rather than assumed. The predecessor tool was
tested by practitioners at an external workshop, and its shortcomings were
recorded in structured feedback.""",
    ),
    (
        """The report currently reports the workshop themes as prose and a table, which
needs no execution environment.""",
        """The report currently reports the feedback themes as prose and a table, which
needs no execution environment.""",
    ),
    (
        'responses = pd.read_csv("data/asilomar_feedback.csv")',
        'responses = pd.read_csv("data/workshop_feedback.csv")',
    ),
    # The table's left column reused participants' own wording; reworded so no
    # phrase in it is traceable to a response, while each finding is unchanged.
    (
        """| Workshop finding | Design consequence |
|---|---|
| Questions feel too academic, obvious, or leading | Let the user pose the question; do not script it |
| UX friction, limited interaction options | Conversational interface, not a form |
| EU/Western regulatory framing may not translate globally | Explicit jurisdiction selection; global instruments always in scope |
| Scope too narrowly focused on partnerships | Answer any question the corpus can support |
| Doesn't fit a real workflow | Run locally, answer on demand, no orchestration required |""",
        """| Feedback finding | Design consequence |
|---|---|
| Questions read as academic and leading | Let the user pose the question; do not script it |
| UX friction, limited interaction options | Conversational interface, not a form |
| EU/Western regulatory framing may not translate globally | Explicit jurisdiction selection; global instruments always in scope |
| Scope confined to partnership review | Answer any question the corpus can support |
| Poor fit with day-to-day work | Run locally, answer on demand, no orchestration required |""",
    ),
    (
        """The free-text responses were more specific still. One table asked for "a more
vector based overall tendence rather than a red flag for a not checked box";
another for a shift "from yes no to text / process". A third argued the tool
should "describe the potential risk exposure of the partnership" instead of
emitting red flags at the end. Several converged independently on an AI
facilitator that could "adapt to circumstances as ethical boundaries and
technologies change".

Two cautions from the same feedback are treated here as binding constraints
rather than aspirations. First: "This tool doesn't replace the need for more
education, collaboration, and experts (human)." Second: the tool should not
"create new mechanisms where some already exist". The system is therefore""",
        """The free-text responses were more specific still. Several asked for graded or
directional output in place of a binary checklist, and for prose and process
rather than yes/no answers. Others argued the tool should characterise a
partnership's risk exposure rather than emit red flags at the end. A number of
respondents converged independently on an assistant able to adapt as ethical
boundaries and technologies change.

Two cautions from the same feedback are treated here as binding constraints
rather than aspirations. First, that a tool of this kind does not remove the
need for education, collaboration, and human expertise. Second, that it should
not build new mechanisms where adequate ones already exist. The system is
therefore""",
    ),

    # Rejoin the sentence the paragraph above ends mid-way through.
    (
        """therefore
scoped as a *reference instrument*""",
        """therefore scoped as a *reference instrument*""",
    ),

    # Put the diagram on its own landscape page. 9in is exactly the width
    # available there (11in paper less the document's two 1in margins), so the
    # figure fills the text block without overhanging it. Rotation alone is not
    # enough: pdflscape rotates the page but leaves the image unscaled.
    (
        """```{mermaid}
%%| label: fig-architecture""",
        """```{=latex}
\\begin{landscape}
```

```{mermaid}
%%| fig-width: 9
%%| label: fig-architecture""",
    ),
    (
        """    class UC,UP eph
```
""",
        """    class UC,UP eph
```

```{=latex}
\\end{landscape}
```
""",
    ),

    # --- scope --------------------------------------------------------------
    (
        """**Out of scope**, deliberately, and consistent with the predecessor tool's own
stated boundaries (workshop slide 16) and the workshop's caution against
over-reach:""",
        """**Out of scope**, deliberately, and consistent with the predecessor tool's own
stated boundaries and the practitioner caution against over-reach:""",
    ),
]

# Terms that must not survive anywhere in the output, checked after replacement.
FORBIDDEN = [
    "IDUN", "Ningen", "Asilomar", "asilomar", "Navigation Tool",
    "workshop slide", "Workshop participants", "Workshop finding",
]


def main() -> int:
    text = SRC.read_text(encoding="utf-8")

    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            print(
                f"ERROR: pattern matched {count} times, expected 1:\n"
                f"  {old[:100]!r}...",
                file=sys.stderr,
            )
            return 1
        text = text.replace(old, new, 1)

    # Any remaining bare citation of the internal workshop report.
    text = re.sub(r" ?\[@asilomar2026workshop\]", "", text)

    leaked = [term for term in FORBIDDEN if term in text]
    if leaked:
        print(f"ERROR: identifying terms survived: {leaked}", file=sys.stderr)
        return 1

    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST.name}")
    print(f"  replacements applied: {len(REPLACEMENTS)}")
    print("  forbidden terms remaining: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
