"""Text normalization shared by every eval grader.

Gold phrases are typed as plain ASCII; real text isn't. Markdown adds
emphasis and heading markers ("**Cognitive liberty**"), PDF extraction leaves
irregular spacing ("evidence -based"), and models write proper Unicode
punctuation — gpt-oss:20b answered "cognitive liberty" using a non-breaking
hyphen (U+2011), which silently defeated a plain ASCII substring match even
though the answer was exactly correct. One normalizer, used everywhere text
gets compared, so retrieval matching and answer grading can't quietly drift
into disagreeing about what counts as "the same text".
"""

import re

# Typographic punctuation a model or a document conversion may use in place of
# the ASCII character a gold phrase is written with.
_PUNCT_MAP = {
    "‘": "'", "’": "'",  # curly single quotes
    "“": '"', "”": '"',  # curly double quotes
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",  # hyphens/dashes
    " ": " ",  # non-breaking space
}


def normalize(text: str) -> str:
    """Lowercase, fold Unicode punctuation to ASCII, strip markdown, collapse whitespace."""
    for src, dst in _PUNCT_MAP.items():
        text = text.replace(src, dst)
    text = re.sub(r"[*_`#>|\\]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()
