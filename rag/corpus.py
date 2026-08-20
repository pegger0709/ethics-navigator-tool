"""What each source document is, and which jurisdiction it belongs to.

The corpus mixes instruments that apply everywhere (UN, UNESCO, OECD) with
ones that bind only in a particular place (GDPR, CCPA). A user in California
should not have their answer shaped by EU regulation they are not subject to,
so documents carry a jurisdiction and retrieval is filtered to the ones the
user selects — plus the global instruments, which always apply.

Display names live here too: filenames like ``397812eng.pdf`` mean nothing to
a reader, and the sidebar and citations should show what the document actually
is.
"""

GLOBAL = "Global"
EU = "European Union"
CALIFORNIA = "California"

# Jurisdictions a user can opt into. GLOBAL is always active and so is not
# offered as a choice.
SELECTABLE_JURISDICTIONS = (EU, CALIFORNIA)

# Keyed by filename *stem*, not full filename: the same document may be held as
# a PDF or as converted markdown, and swapping formats must not change its
# identity, title, or jurisdiction.
DOCUMENTS: dict[str, tuple[str, str]] = {
    "UN_declaration_HumanRights": (
        "Universal Declaration of Human Rights",
        GLOBAL,
    ),
    "UNESCO_397812eng": (
        "UNESCO Recommendation on the Ethics of Neurotechnology",
        GLOBAL,
    ),
    "OECD-LEGAL-0457-en": (
        "OECD Recommendation on Responsible Innovation in Neurotechnology",
        GLOBAL,
    ),
    "GuidingPrinciplesBusinessHR_EN": (
        "UN Guiding Principles on Business and Human Rights",
        GLOBAL,
    ),
    "EU_GDPR": (
        "EU General Data Protection Regulation (GDPR)",
        EU,
    ),
    "EU_AIAct": (
        "EU Artificial Intelligence Act",
        EU,
    ),
    "ccpa_statute": (
        "California Consumer Privacy Act (CCPA)",
        CALIFORNIA,
    ),
}


def stem(source: str) -> str:
    """Filename without its extension — the key documents are known by."""
    return source.rsplit(".", 1)[0]


def display_name(source: str) -> str:
    """Human-readable title for ``source``.

    Documents a user uploads themselves are not in the registry, so fall back
    to a tidied filename rather than hiding them.
    """
    key = stem(source)
    if key in DOCUMENTS:
        return DOCUMENTS[key][0]
    return key.replace("_", " ").replace("-", " ").strip()


def jurisdiction_of(source: str) -> str:
    """Jurisdiction for ``source``; uploads default to global."""
    return DOCUMENTS.get(stem(source), (None, GLOBAL))[1]


def active_jurisdictions(selected: list[str] | tuple[str, ...] | None) -> list[str]:
    """Jurisdictions to retrieve from: the global instruments plus ``selected``."""
    return [GLOBAL, *(selected or ())]


def group_by_jurisdiction(sources: list[str]) -> dict[str, list[str]]:
    """Group source filenames by jurisdiction, each list sorted by display name."""
    grouped: dict[str, list[str]] = {}
    for source in sources:
        grouped.setdefault(jurisdiction_of(source), []).append(source)
    for group in grouped.values():
        group.sort(key=display_name)
    return grouped
