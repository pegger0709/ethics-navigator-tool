"""Pre-computed per-document digests, for questions retrieval cannot answer.

Similarity search is good at "what is cognitive liberty?" — one passage holds
the answer and it ranks first. It is structurally incapable of "summarize every
principle": the answer is spread over dozens of passages that each look only
mildly relevant to an abstract query. Measured on this corpus, a broad question
retrieved 0 of 3 known-relevant passages at k=50, and needed k=200 of 521
chunks to reach 2 of 3.

So broad questions are answered from digests built ahead of time instead. Each
document is read once in order, in windows, and each window is condensed into
the statements it makes. The digests are stored as ``KIND_SUMMARY`` chunks, so
broad questions retrieve dense principle statements rather than raw fragments.

This is deliberately a separate command rather than part of startup ingestion:
it costs tens of minutes of CPU inference, and a colleague's first launch must
not hang on it.

    python -m rag.summaries                        # every document lacking a digest
    python -m rag.summaries --source EU_GDPR.pdf   # just one (long ones take hours)
    python -m rag.summaries --rebuild              # discard existing digests and redo
"""

import argparse
import time

from llm import ollama_client
from rag.embeddings import (
    KIND_CONTENT,
    KIND_SUMMARY,
    _sources_in,
    get_collection,
    upsert_chunks,
)

# How much document text to condense per call. Small enough that CPU inference
# stays tractable, large enough that a window holds several related provisions.
WINDOW_CHARS = 6000

SUMMARY_PROMPT = (
    "Below is an excerpt from a policy document. List every distinct "
    "principle, rule, definition or requirement it states.\n\n"
    "Rules:\n"
    "- One item per line, each a complete standalone sentence.\n"
    "- Keep the document's own terminology, including any names or numbers it "
    "uses for its provisions.\n"
    "- State only what the excerpt says. Add nothing.\n"
    "- If the excerpt is only front matter, page furniture, citations or a "
    "table of contents, reply with exactly: NONE\n\n"
    "EXCERPT:\n{excerpt}"
)


def _windows(chunks: list[str], size: int = WINDOW_CHARS) -> list[str]:
    """Group ordered chunks into windows of roughly ``size`` characters."""
    windows: list[str] = []
    current: list[str] = []
    current_len = 0
    for chunk in chunks:
        if current and current_len + len(chunk) > size:
            windows.append("\n".join(current))
            current, current_len = [], 0
        current.append(chunk)
        current_len += len(chunk)
    if current:
        windows.append("\n".join(current))
    return windows


def _content_chunks(collection, source: str) -> list[str]:
    """Return one document's content chunks in document order."""
    results = collection.get(
        where={"$and": [{"source": source}, {"kind": KIND_CONTENT}]},
        include=["documents"],
    )
    ids, documents = results["ids"], results["documents"]
    # Chroma does not guarantee ordering; ids end in the chunk index.
    ordered = sorted(zip(ids, documents), key=lambda pair: int(pair[0].rsplit(":", 1)[1]))
    return [doc for _, doc in ordered]


def summarise_document(collection, source: str) -> int:
    """Build and store the digest for one document. Returns lines written."""
    chunks = _content_chunks(collection, source)
    windows = _windows(chunks)
    print(f"  {source}: {len(chunks)} chunks -> {len(windows)} windows", flush=True)

    lines: list[str] = []
    for index, window in enumerate(windows, 1):
        started = time.time()
        messages = [{"role": "user", "content": SUMMARY_PROMPT.format(excerpt=window)}]
        try:
            raw = ollama_client.chat(messages, stream=False, num_ctx=8192) or ""
        except Exception as exc:  # noqa: BLE001 — one bad window must not lose the rest
            print(f"    window {index}: FAILED ({type(exc).__name__}: {exc})", flush=True)
            continue

        window_lines = [
            line.strip().lstrip("-*• ").strip()
            for line in raw.splitlines()
            if line.strip() and line.strip().upper() != "NONE"
        ]
        window_lines = [line for line in window_lines if len(line) > 25]
        lines.extend(window_lines)
        print(f"    window {index}/{len(windows)}: {len(window_lines)} items "
              f"({time.time() - started:.0f}s)", flush=True)

    if not lines:
        return 0

    # Pack the digest into retrievable chunks. Several statements per chunk
    # keeps related principles together without recreating the dilution that
    # made raw content chunks unsearchable.
    digest_chunks: list[str] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if sum(len(item) for item in current) > 700:
            digest_chunks.append("\n".join(current))
            current = []
    if current:
        digest_chunks.append("\n".join(current))

    upsert_chunks(collection, digest_chunks, source, KIND_SUMMARY)
    print(f"  {source}: {len(lines)} statements -> {len(digest_chunks)} digest chunks",
          flush=True)
    return len(lines)


def build_summaries(rebuild: bool = False, only: tuple[str, ...] | None = None) -> int:
    """Build digests for indexed documents. Returns total statements.

    ``only`` restricts the run to specific source filenames. Cost scales with
    document length — a long statute can take hours on CPU — so building the
    corpus one document at a time is often the practical path.
    """
    collection = get_collection()
    content_sources = _sources_in(collection, KIND_CONTENT)
    existing = _sources_in(collection, KIND_SUMMARY)

    if only:
        unknown = set(only) - content_sources
        if unknown:
            print(f"not indexed, skipping: {sorted(unknown)}")
        content_sources = content_sources & set(only)

    if rebuild and existing:
        targets = (existing & content_sources) if only else existing
        if targets:
            print(f"discarding existing digests for {len(targets)} document(s)")
            collection.delete(
                where={"$and": [{"kind": KIND_SUMMARY}, {"source": {"$in": sorted(targets)}}]}
            )
            existing = existing - targets

    pending = sorted(content_sources - existing)
    if not pending:
        print("nothing to build; use --rebuild to redo existing digests")
        return 0

    print(f"building digests for {len(pending)} document(s) with "
          f"{ollama_client.CHAT_MODEL}")
    total = 0
    for source in pending:
        total += summarise_document(collection, source)
    return total


def summaries_available() -> bool:
    """True when at least one document has a stored digest."""
    return bool(_sources_in(get_collection(), KIND_SUMMARY))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true", help="discard existing digests first")
    parser.add_argument(
        "--source",
        action="append",
        help="only build this document (repeatable); defaults to all pending",
    )
    args = parser.parse_args()

    started = time.time()
    total = build_summaries(rebuild=args.rebuild, only=tuple(args.source) if args.source else None)
    print(f"\n{total} statements in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
