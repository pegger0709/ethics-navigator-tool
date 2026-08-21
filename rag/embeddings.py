"""Chroma collection setup and document ingestion.

Embedding is delegated to Chroma's ``OllamaEmbeddingFunction`` attached to the
collection, so both ingestion and query-time embedding share one code path and
go through the local Ollama service.
"""

import hashlib
import io
import os
import re

import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from dotenv import load_dotenv
from pypdf import PdfReader

from llm.ollama_client import EMBED_MODEL, OLLAMA_HOST
from rag.corpus import jurisdiction_of

load_dotenv()

COLLECTION_NAME = "ethics_docs"
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "data/documents")
# Digests are plain-text files, one per source document, committed to the repo.
# Keeping them on disk rather than only in Chroma means they survive the vector
# store being rebuilt, and ship with the app so nobody regenerates them.
DIGESTS_DIR = os.getenv("DIGESTS_DIR", "data/digests")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
# CPU-only embedding of a large batch can take a while; the client default (60s)
# is too tight for that, so it's raised and left configurable.
EMBED_TIMEOUT = int(os.getenv("EMBED_TIMEOUT", "300"))


def get_chroma_client():
    """Return a Chroma client.

    Uses an HTTP client when ``CHROMA_HOST`` is set (the Docker stack runs Chroma
    as its own service); otherwise a persistent local client backed by
    ``CHROMA_PERSIST_DIR``. The in-memory client is never used.
    """
    host = os.getenv("CHROMA_HOST")
    if host:
        port = int(os.getenv("CHROMA_PORT", "8000"))
        return chromadb.HttpClient(host=host, port=port)
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_collection():
    """Get-or-create the documents collection with the Ollama embedder."""
    client = get_chroma_client()
    embedder = OllamaEmbeddingFunction(
        url=OLLAMA_HOST, model_name=EMBED_MODEL, timeout=EMBED_TIMEOUT
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedder
    )


def extract_text(filename: str, data: bytes) -> str:
    """Extract plain text from a document's raw bytes by extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext in {".txt", ".md"}:
        return data.decode("utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {filename}")


CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))


def chunk_text(
    text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Split text into chunks that respect line boundaries.

    Cutting at a fixed character offset packed many self-contained units into
    one chunk — the OECD definitions list put six definitions in a single
    chunk, so its embedding averaged all six and a query for any one of them
    matched only weakly. Retrieval recall for such passages was near zero
    regardless of how large ``k`` grew.

    Packing whole lines instead keeps definitions and numbered paragraphs
    intact. Overlap carries trailing lines into the next chunk so statements
    split across a boundary are still reachable.
    """
    if size <= overlap:
        raise ValueError("size must be greater than overlap")

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> list[str]:
        """Emit the current chunk and return the lines to carry over."""
        chunks.append("\n".join(current))
        carry: list[str] = []
        carry_len = 0
        for previous in reversed(current):
            if carry_len + len(previous) + 1 > overlap:
                break
            carry.insert(0, previous)
            carry_len += len(previous) + 1
        return carry

    for line in lines:
        # A single line longer than the target can't be packed; split it on
        # character boundaries rather than emitting one oversized chunk.
        while len(line) > size:
            if current:
                current = flush()
                current_len = sum(len(item) + 1 for item in current)
            chunks.append(line[:size])
            line = line[size - overlap :]

        if current and current_len + len(line) + 1 > size:
            current = flush()
            current_len = sum(len(item) + 1 for item in current)

        current.append(line)
        current_len += len(line) + 1

    if current:
        chunks.append("\n".join(current))
    return [chunk for chunk in chunks if chunk.strip()]


UPSERT_BATCH_SIZE = 100

# Chunks are tagged so the two question types can be retrieved separately:
# verbatim excerpts answer specific questions, condensed digests answer broad
# ones. Similarity search over raw excerpts cannot answer "summarize every
# principle" at any practical k — measured at 0/3 gold passages up to k=50.
KIND_CONTENT = "content"
KIND_SUMMARY = "summary"


def upsert_chunks(
    collection,
    chunks: list[str],
    source: str,
    kind: str = KIND_CONTENT,
    extra_metadata: dict | None = None,
) -> int:
    """Upsert ``chunks`` in batches, tagged with ``source`` and ``kind``.

    Large documents can produce thousands of chunks; embedding them in one call
    risks a client-side timeout on a CPU-only Ollama backend, so upserts are
    split into smaller batches (see Chroma's guidance: 50-250 per batch).
    """
    prefix = source if kind == KIND_CONTENT else f"{source}:{kind}"
    ids = [f"{prefix}:{i}" for i in range(len(chunks))]
    metadata = {
        "source": source,
        "kind": kind,
        "jurisdiction": jurisdiction_of(source),
        **(extra_metadata or {}),
    }
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        end = start + UPSERT_BATCH_SIZE
        batch = chunks[start:end]
        collection.upsert(
            ids=ids[start:end],
            documents=batch,
            metadatas=[dict(metadata) for _ in batch],
        )
    return len(chunks)


def _add_document(collection, text: str, source: str) -> int:
    """Chunk one document's text and upsert it. Returns the chunk count."""
    return upsert_chunks(collection, chunk_text(text), source, KIND_CONTENT)


DIGEST_CHUNK_CHARS = 700


def pack_statements(lines: list[str], size: int = DIGEST_CHUNK_CHARS) -> list[str]:
    """Group digest statements into retrievable chunks.

    Several statements per chunk keeps related provisions together without
    recreating the dilution that made raw content chunks unsearchable.
    """
    chunks: list[str] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if sum(len(item) for item in current) > size:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks


def read_digest_statements(path: str) -> list[str]:
    """Read one digest file into individual statements.

    Tolerates the list markers and headings a chat model tends to emit, and
    drops fragments too short to be a real statement.
    """
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()
    statements = []
    for line in raw.splitlines():
        line = line.strip().lstrip("-*•#> ").strip()
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if len(line) > 25:
            statements.append(line)
    return statements


def load_digests(directory: str = DIGESTS_DIR) -> dict[str, list[str]]:
    """Map source filename -> digest statements, from ``directory``.

    A digest file is matched to its document by filename stem, so
    ``data/digests/EU_GDPR.md`` is the digest of ``data/documents/EU_GDPR.pdf``.
    """
    digests: dict[str, list[str]] = {}
    if not os.path.isdir(directory):
        return digests
    stems = {
        os.path.splitext(name)[0]: name
        for name in os.listdir(DOCUMENTS_DIR)
        if os.path.isfile(os.path.join(DOCUMENTS_DIR, name))
    }
    for filename in sorted(os.listdir(directory)):
        path = os.path.join(directory, filename)
        stem, ext = os.path.splitext(filename)
        if not os.path.isfile(path) or ext.lower() not in {".txt", ".md"}:
            continue
        source = stems.get(stem)
        if source is None:
            print(f"digest '{filename}' has no matching document; skipping")
            continue
        statements = read_digest_statements(path)
        if statements:
            digests[source] = statements
    return digests


def load_documents(directory: str = DOCUMENTS_DIR) -> list[tuple[str, str]]:
    """Read every supported file in ``directory`` into ``(text, filename)`` pairs."""
    pairs = []
    if not os.path.isdir(directory):
        return pairs
    for filename in sorted(os.listdir(directory)):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        if os.path.splitext(filename)[1].lower() not in SUPPORTED_EXTENSIONS:
            continue
        with open(path, "rb") as handle:
            pairs.append((extract_text(filename, handle.read()), filename))
    return pairs


def ingest(directory: str = DOCUMENTS_DIR) -> int:
    """Sync Chroma with ``directory``: index new documents, prune removed ones.

    Skipping already-indexed sources (rather than gating on "is the collection
    empty") makes this resumable: a restart after a partial failure only redoes
    the document that didn't finish, and dropping in a new file gets it indexed
    without needing to clear the whole knowledge base first. Sources that are
    indexed but no longer on disk (deleted or renamed) are removed, so
    replacing a document doesn't leave its old chunks behind permanently.
    Returns the number of chunks added.
    """
    collection = get_collection()
    on_disk = load_documents(directory)
    on_disk_sources = {source for _, source in on_disk}
    already_indexed = _sources_in(collection)

    stale_sources = already_indexed - on_disk_sources
    if stale_sources:
        collection.delete(where={"source": {"$in": list(stale_sources)}})

    total = 0
    for text, source in on_disk:
        if source in already_indexed:
            continue
        total += _add_document(collection, text, source)

    total += _sync_digests(collection, on_disk_sources)
    return total


def _digest_hash(statements: list[str]) -> str:
    """Fingerprint of a digest's content, used to detect an edited file."""
    return hashlib.md5("\n".join(statements).encode("utf-8")).hexdigest()


def _indexed_digest_hashes(collection) -> dict[str, str]:
    """Map source -> stored content hash, for every currently indexed digest."""
    results = collection.get(where={"kind": KIND_SUMMARY}, include=["metadatas"])
    hashes: dict[str, str] = {}
    for meta in results["metadatas"]:
        hashes.setdefault((meta or {}).get("source"), (meta or {}).get("digest_hash"))
    return hashes


def _sync_digests(collection, on_disk_sources: set[str]) -> int:
    """Index every digest file that is new or has changed since last indexed.

    Because digests are files rather than only rows in Chroma, wiping the
    vector store no longer destroys them: the next ingest restores them. A
    content hash (not just presence) decides whether to (re)index, so editing
    a digest file — e.g. regenerating it for better quality — takes effect on
    the next ingest instead of being silently skipped because *a* digest for
    that source already existed.
    """
    digests = load_digests()
    indexed_hashes = _indexed_digest_hashes(collection)
    total = 0
    for source, statements in digests.items():
        if source not in on_disk_sources:
            continue
        new_hash = _digest_hash(statements)
        if indexed_hashes.get(source) == new_hash:
            continue
        if source in indexed_hashes:
            collection.delete(where={"$and": [{"kind": KIND_SUMMARY}, {"source": source}]})
            print(f"digest for {source} changed; replacing indexed version")
        chunks = pack_statements(statements)
        total += upsert_chunks(
            collection, chunks, source, KIND_SUMMARY, extra_metadata={"digest_hash": new_hash}
        )
        print(f"loaded digest for {source}: {len(statements)} statements "
              f"-> {len(chunks)} chunks")
    return total


def ingest_uploads(uploaded_files) -> int:
    """Ingest files from the Streamlit uploader.

    Each file is also saved into ``DOCUMENTS_DIR`` so the corpus persists across
    restarts (the directory is a mounted volume in Docker). Returns total chunks.
    """
    collection = get_collection()
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    total = 0
    for uploaded in uploaded_files:
        data = uploaded.getvalue()
        # basename strips any directory components a crafted upload name might
        # carry, keeping writes inside DOCUMENTS_DIR.
        safe_name = os.path.basename(uploaded.name)
        if not safe_name or safe_name in (".", ".."):
            continue  # skip names that don't resolve to a real file
        with open(os.path.join(DOCUMENTS_DIR, safe_name), "wb") as handle:
            handle.write(data)
        total += _add_document(collection, extract_text(safe_name, data), safe_name)
    return total


def _sources_in(collection, kind: str | None = KIND_CONTENT) -> set[str]:
    """Return unique source filenames in ``collection``, optionally by kind.

    Defaults to content chunks: a document whose summary exists but whose text
    does not has not really been ingested, and must not be skipped by
    :func:`ingest`.
    """
    where = {"kind": kind} if kind else None
    results = collection.get(include=["metadatas"], where=where)
    return {(m or {}).get("source", "unknown") for m in results["metadatas"]}


def list_sources() -> list[str]:
    """Return sorted unique source filenames currently in the collection."""
    return sorted(_sources_in(get_collection()))


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested {count} chunks from '{DOCUMENTS_DIR}' into '{COLLECTION_NAME}'.")
