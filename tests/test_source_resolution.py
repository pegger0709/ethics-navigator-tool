"""One file per document: format duplicates must never both be indexed.

These are pure filesystem tests — no Chroma, no Ollama — so they cost
milliseconds and run in the fast gate. They exist because the failure they
guard against is silent: indexing a document twice does not raise, does not
change any answer's shape, and only shows up as a chunk count that has
quietly doubled.
"""

import os

import pytest

from rag import corpus, embeddings


def write(directory, name, body=b"placeholder text"):
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        handle.write(body)
    return path


@pytest.fixture()
def docs_dir(tmp_path):
    return str(tmp_path)


def test_prefers_markdown_over_pdf(docs_dir):
    """The converted markdown is the index source; the PDF is the archive copy."""
    write(docs_dir, "EU_GDPR.md")
    write(docs_dir, "EU_GDPR.pdf")

    resolved = embeddings.resolve_sources(docs_dir)

    assert resolved == {"EU_GDPR": "EU_GDPR.md"}


def test_pdf_used_when_it_is_the_only_format(docs_dir):
    """Documents held only as PDF are still indexed."""
    write(docs_dir, "OECD-LEGAL-0457-en.pdf")

    resolved = embeddings.resolve_sources(docs_dir)

    assert resolved == {"OECD-LEGAL-0457-en": "OECD-LEGAL-0457-en.pdf"}


def test_txt_outranks_pdf_but_not_markdown(docs_dir):
    write(docs_dir, "notes.txt")
    write(docs_dir, "notes.pdf")
    assert embeddings.resolve_sources(docs_dir) == {"notes": "notes.txt"}

    write(docs_dir, "notes.md")
    assert embeddings.resolve_sources(docs_dir) == {"notes": "notes.md"}


def test_one_entry_per_document_across_the_whole_corpus(docs_dir):
    """Every registered document, held in both formats, resolves to one file."""
    for stem in corpus.DOCUMENTS:
        write(docs_dir, f"{stem}.md")
        write(docs_dir, f"{stem}.pdf")

    resolved = embeddings.resolve_sources(docs_dir)

    assert len(resolved) == len(corpus.DOCUMENTS)
    assert set(resolved) == set(corpus.DOCUMENTS)
    assert all(name.endswith(".md") for name in resolved.values())


def test_load_documents_reads_each_document_once(docs_dir):
    """The guard has to hold at the point that actually feeds the index."""
    write(docs_dir, "UN_declaration_HumanRights.md", b"# Article 24\nRest and leisure.")
    write(docs_dir, "UN_declaration_HumanRights.pdf", b"%PDF-1.4 irrelevant")

    pairs = embeddings.load_documents(docs_dir)

    assert [source for _, source in pairs] == ["UN_declaration_HumanRights.md"]


def test_unsupported_extensions_are_ignored(docs_dir):
    write(docs_dir, "UN_declaration_HumanRights.md")
    write(docs_dir, "UN_declaration_HumanRights.docx")

    assert embeddings.resolve_sources(docs_dir) == {
        "UN_declaration_HumanRights": "UN_declaration_HumanRights.md"
    }


def test_missing_directory_is_not_an_error(tmp_path):
    assert embeddings.resolve_sources(str(tmp_path / "nope")) == {}
