"""Query logic: embed query -> retrieve chunks -> build prompt -> answer."""

from llm import ollama_client
from rag.embeddings import get_collection

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
    results = get_collection().query(query_texts=[query], n_results=k)
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


def answer(query: str, history: list[dict] | None = None, k: int = 4):
    """Retrieve context and stream an answer.

    Returns ``(token_stream, chunks)`` where ``token_stream`` is a generator of
    content tokens and ``chunks`` are the retrieved sources for display.
    """
    history = history or []
    chunks = retrieve(query, k=k)
    messages = build_messages(query, chunks, history)
    return ollama_client.chat(messages, stream=True), chunks
