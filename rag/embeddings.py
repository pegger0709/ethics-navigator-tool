"""Chroma collection setup and document ingestion.

Embedding is delegated to Chroma's ``OllamaEmbeddingFunction`` attached to the
collection, so both ingestion and query-time embedding share one code path and
go through the local Ollama service.
"""

import io
import os

import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from dotenv import load_dotenv
from pypdf import PdfReader

from llm.ollama_client import EMBED_MODEL, OLLAMA_HOST

load_dotenv()

COLLECTION_NAME = "ethics_docs"
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "data/documents")
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


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    """Split text into overlapping character chunks, skipping empty ones."""
    if size <= overlap:
        raise ValueError("size must be greater than overlap")
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + size].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks


UPSERT_BATCH_SIZE = 100


def _add_document(collection, text: str, source: str) -> int:
    """Chunk one document's text and upsert it in batches. Returns the chunk count.

    Large documents can produce thousands of chunks; embedding them in one call
    risks a client-side timeout on a CPU-only Ollama backend, so upserts are
    split into smaller batches (see Chroma's guidance: 50-250 per batch).
    """
    chunks = chunk_text(text)
    ids = [f"{source}:{i}" for i in range(len(chunks))]
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        end = start + UPSERT_BATCH_SIZE
        batch = chunks[start:end]
        collection.upsert(
            ids=ids[start:end],
            documents=batch,
            metadatas=[{"source": source} for _ in batch],
        )
    return len(chunks)


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


def _sources_in(collection) -> set[str]:
    """Return the set of unique source filenames already in ``collection``."""
    results = collection.get(include=["metadatas"])
    return {(m or {}).get("source", "unknown") for m in results["metadatas"]}


def list_sources() -> list[str]:
    """Return sorted unique source filenames currently in the collection."""
    return sorted(_sources_in(get_collection()))


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested {count} chunks from '{DOCUMENTS_DIR}' into '{COLLECTION_NAME}'.")
