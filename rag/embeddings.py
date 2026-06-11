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
    embedder = OllamaEmbeddingFunction(url=OLLAMA_HOST, model_name=EMBED_MODEL)
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


def _add_document(collection, text: str, source: str) -> int:
    """Chunk one document's text and upsert it. Returns the chunk count."""
    chunks = chunk_text(text)
    if not chunks:
        return 0
    collection.upsert(
        ids=[f"{source}:{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"source": source} for _ in chunks],
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
    """Ingest every document in ``directory`` into Chroma. Returns total chunks."""
    collection = get_collection()
    total = 0
    for text, source in load_documents(directory):
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


def list_sources() -> list[str]:
    """Return sorted unique source filenames currently in the collection."""
    results = get_collection().get(include=["metadatas"])
    sources = {(m or {}).get("source", "unknown") for m in results["metadatas"]}
    return sorted(sources)


def collection_is_empty() -> bool:
    """True when the collection has no documents yet."""
    return get_collection().count() == 0


def clear_knowledge_base(directory: str = DOCUMENTS_DIR) -> None:
    """Remove all indexed documents and delete saved files from the documents folder.

    Deletes documents by ID rather than destroying and recreating the collection,
    so all operations go through a single client instance with consistent state.
    """
    collection = get_collection()
    all_ids = collection.get(include=[])["ids"]
    if all_ids:
        collection.delete(ids=all_ids)
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if filename == ".gitkeep":
                continue
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                os.remove(path)


if __name__ == "__main__":
    count = ingest()
    print(f"Ingested {count} chunks from '{DOCUMENTS_DIR}' into '{COLLECTION_NAME}'.")
