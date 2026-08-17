"""Query logic: embed query -> retrieve chunks -> build prompt -> answer."""

from llm import ollama_client
from rag.embeddings import get_collection

DEFAULT_NUM_CTX = 2048  # Ollama's own default, used as a floor
RESPONSE_MARGIN_TOKENS = 1024  # headroom for the model's own answer
CHARS_PER_TOKEN = 4  # rough estimate, good enough for sizing the context window

SYSTEM_PROMPT = (
    "You are Ethics Navigator, an assistant that answers questions using only "
    "the provided context excerpts from the user's documents. Follow these rules:\n"
    "- Base your answer solely on the context below. Do not use outside knowledge.\n"
    "- If the context is relevant, draw the reasonable inference and give a direct, "
    "committed answer — even if the wording does not exactly match the question. "
    "Do not hedge with 'I don't know' when the context supports a clear conclusion.\n"
    "- Only say you don't know if the context is genuinely unrelated to the question.\n"
    "- Cite the source filename(s) you relied on, in parentheses."
)


def retrieve(query: str, k: int = 4) -> list[dict]:
    """Return the top-``k`` chunks for ``query`` as ``{text, source}`` dicts."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(k, count))
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    chunks = []
    for text, meta in zip(documents, metadatas):
        chunks.append({"text": text, "source": (meta or {}).get("source", "unknown")})
    return chunks


def build_messages(query: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    """Assemble the message list: system prompt + context, prior turns, query."""
    if chunks:
        context = "\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in chunks
        )
    else:
        context = "(no relevant context found)"

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": query})
    return messages


def _num_ctx_for(messages: list[dict]) -> int:
    """Size the context window to fit ``messages`` plus room for the answer.

    Ollama's fixed default (2048 tokens) is fine for small ``top_k`` but starts
    silently truncating the retrieved context once more chunks are requested,
    which would otherwise defeat the point of raising ``top_k`` at all.
    """
    total_chars = sum(len(m["content"]) for m in messages)
    estimated_tokens = total_chars // CHARS_PER_TOKEN
    return max(DEFAULT_NUM_CTX, estimated_tokens + RESPONSE_MARGIN_TOKENS)


def answer(query: str, history: list[dict] | None = None, k: int = 4):
    """Retrieve context and stream an answer.

    Returns ``(token_stream, chunks)`` where ``token_stream`` is a generator of
    content tokens and ``chunks`` are the retrieved sources for display.
    """
    history = history or []
    chunks = retrieve(query, k=k)
    messages = build_messages(query, chunks, history)
    num_ctx = _num_ctx_for(messages)
    return ollama_client.chat(messages, stream=True, num_ctx=num_ctx), chunks
