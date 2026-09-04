"""Publisher/administrative boilerplate is stripped before chunking, and
nothing else is.

Pure text-transform tests — no Chroma, no Ollama — so they cost milliseconds
and run in the fast gate. The two directions both matter here: the OECD
document's front matter and back matter used to outrank its own operative
text at retrieval time (see report/ "oecd-due-regard"), but a naive fix that
deletes a whole section by heading name is just as capable of eating real
content that happens to share a heading's boundary — which is exactly what
happened to GuidingPrinciplesBusinessHR_EN's provenance paragraph during
development of this fix. Both failure directions get a regression test.
"""

from rag.embeddings import strip_boilerplate


def test_oecd_front_matter_removed():
    text = (
        "# Recommendation of the Council on Responsible Innovation\n\n"
        "OECD Legal Instruments\n\n"
        "**Please cite this document as:**\n"
        "OECD, *Recommendation*, OECD/LEGAL/0457\n\n"
        "**Photo credit:** (c) Adobe Stock\n\n"
        "(c) OECD 2025\n\n"
        "This document is provided free of charge. It may be reproduced and "
        "distributed free of charge without requiring any further permissions, "
        "as long as it is not altered in any way. It may not be sold.\n\n"
        "## Background Information\n\n"
        "The Recommendation was adopted by the OECD Council in 2019.\n"
    )
    stripped = strip_boilerplate(text)

    assert "Please cite this document as" not in stripped
    assert "Photo credit" not in stripped
    assert "reproduced and distributed free of charge" not in stripped
    assert "The Recommendation was adopted by the OECD Council in 2019." in stripped


def test_oecd_back_matter_removed_to_end_of_document():
    text = (
        "# Title\n\n"
        "## Operative Section\n\n"
        "d) Avoid harm, and show due regard for human rights and societal "
        "values, especially privacy, cognitive liberty, and autonomy of "
        "individuals.\n\n"
        "## About the OECD\n\n"
        "The OECD is a unique forum where governments work together to "
        "address the economic, social and environmental challenges of "
        "globalisation.\n\n"
        "## OECD Legal Instruments\n\n"
        "All substantive OECD legal instruments, whether in force or "
        "abrogated, are listed in the online Compendium.\n"
    )
    stripped = strip_boilerplate(text)

    assert "show due regard for human rights" in stripped
    assert "unique forum" not in stripped
    assert "Compendium" not in stripped


def test_front_matter_without_boilerplate_markers_is_kept():
    """An un-headed intro block is only removed when it matches a known
    publisher/rights phrase — not merely for being un-headed."""
    text = (
        "# A Document\n\n"
        "This introductory paragraph is genuine context about the document's "
        "purpose, not administrative boilerplate.\n\n"
        "## First Section\n\n"
        "Some content.\n"
    )
    stripped = strip_boilerplate(text)

    assert "genuine context about the document's purpose" in stripped


def test_a_heading_matching_a_boilerplate_title_is_kept_if_its_body_is_not_boilerplate():
    """'Note' is only publisher boilerplate when its content says so — a
    document with a substantive section that happens to be titled 'Note'
    must not be silently deleted."""
    text = (
        "# A Document\n\n"
        "## Note\n\n"
        "This note clarifies that the obligation applies retroactively.\n\n"
        "## Next Section\n\n"
        "More content.\n"
    )
    stripped = strip_boilerplate(text)

    assert "obligation applies retroactively" in stripped


def test_table_of_contents_entries_removed_but_trailing_prose_kept():
    """Regression: a table of contents heading does not reliably bound a
    table-of-contents *section*. The first version of this fix deleted
    everything up to the next heading, which took a genuine provenance
    paragraph with it because nothing separated it from the entry list."""
    text = (
        "# Guiding Principles on Business and Human Rights\n\n"
        "## Note\n\n"
        "(c) 2011 United Nations\n\n"
        "All worldwide rights reserved\n\n"
        "## Contents\n\n"
        "I. THE STATE DUTY TO PROTECT HUMAN RIGHTS 3\n"
        "A. Foundational principles 3\n"
        "B. Operational principles 4\n\n"
        "This publication contains the Guiding Principles on Business and "
        "Human Rights, developed by the Special Representative.\n\n"
        "The Human Rights Council endorsed the Guiding Principles in 2011.\n\n"
        "## General principles\n\n"
        "These Guiding Principles are grounded in recognition of States' "
        "existing obligations.\n"
    )
    stripped = strip_boilerplate(text)

    assert "THE STATE DUTY TO PROTECT HUMAN RIGHTS 3" not in stripped
    assert "Foundational principles 3" not in stripped
    assert "All worldwide rights reserved" not in stripped
    assert "This publication contains the Guiding Principles" in stripped
    assert "The Human Rights Council endorsed the Guiding Principles" in stripped
    assert "grounded in recognition of States' existing obligations" in stripped


def test_ccpa_style_dot_leader_toc_entries_removed():
    text = (
        "# CALIFORNIA CONSUMER PRIVACY ACT OF 2018\n\n"
        "## Contents\n\n"
        "1798.100. General Duties of Businesses"
        "................................. 3\n"
        "1798.105. Consumers' Right to Delete Personal Information"
        "....................... 4\n\n"
        "### 1798.100. General Duties of Businesses that Collect Personal Information\n\n"
        "(a) A business that controls the collection of personal information "
        "shall disclose its practices.\n"
    )
    stripped = strip_boilerplate(text)

    assert "................................. 3" not in stripped
    assert "### 1798.100. General Duties of Businesses that Collect Personal Information" in stripped
    assert "shall disclose its practices" in stripped


def test_documents_without_boilerplate_are_untouched():
    text = (
        "# REGULATION (EU) 2016/679\n\n"
        "## PREAMBLE\n\n"
        "(1) The protection of natural persons is a fundamental right.\n\n"
        "## CHAPTER I\n\n"
        "## General provisions\n\n"
        "Article 1\n"
        "This Regulation lays down rules.\n"
    )
    assert strip_boilerplate(text).rstrip("\n") == text.rstrip("\n")


def test_document_with_no_headings_is_untouched():
    text = "Just plain text with no markdown headings at all.\n"
    assert strip_boilerplate(text) == text


def test_single_heading_document_is_untouched():
    """A document with only its title heading has no front-matter boundary
    and no second heading to bound anything against — must not crash or
    delete the whole document."""
    text = "# Universal Declaration of Human Rights\n\nArticle 1\nAll human beings...\n"
    assert strip_boilerplate(text).rstrip("\n") == text.rstrip("\n")
