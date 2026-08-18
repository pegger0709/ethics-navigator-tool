"""Query logic: embed query -> retrieve chunks -> build prompt -> answer."""

import os
import re

from llm import ollama_client
from rag.embeddings import get_collection

DEFAULT_NUM_CTX = 2048  # Ollama's own default, used as a floor
RESPONSE_MARGIN_TOKENS = 1024  # headroom for the model's own answer
CHARS_PER_TOKEN = 4  # rough estimate, good enough for sizing the context window

# Hard ceiling on prompt size. The model itself allows far more, but every
# extra token costs CPU time, so conversation history is trimmed to fit this
# rather than being allowed to grow without bound.
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "8192"))

# Named retrieval modes. Broad questions need many chunks and sub-query
# decomposition to cover a document evenly; narrow factual ones are answered
# from a couple of chunks and only pay latency for the extras.
MODES: dict[str, dict] = {
    "Simple question answering": {
        "k": 4,
        "multi_query": False,
        "hint": "Fastest. For specific facts stated in one place.",
    },
    "Deeper questions": {
        "k": 12,
        "multi_query": True,
        "hint": "Slower. For questions spanning a few parts of a document.",
    },
    "Broad synthesis": {
        "k": 30,
        "multi_query": True,
        "hint": "Slowest. For 'summarize everything about X' questions.",
    },
}
DEFAULT_MODE = "Simple question answering"

# Kept small deliberately: each extra sub-query lengthens the decomposition
# response *and* widens the merged context, so both LLM calls get slower.
MAX_SUBQUERIES = 3
MIN_CHUNKS_PER_SUBQUERY = 3

DECOMPOSE_PROMPT = (
    "You turn a user's question into targeted search queries for a document "
    "search engine. Write one short query per line, each covering a distinct "
    "aspect of the question. Use the concrete vocabulary the source documents "
    "would use, not the abstract wording of the question. Output at most "
    "{max_n} lines, with no numbering, no bullets and no commentary — just the "
    "queries themselves."
)

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
    """Return the top-``k`` chunks for ``query`` as ``{id, text, source, distance}`` dicts."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(k, count))
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    chunks = []
    for chunk_id, text, meta, distance in zip(ids, documents, metadatas, distances):
        chunks.append(
            {
                "id": chunk_id,
                "text": text,
                "source": (meta or {}).get("source", "unknown"),
                "distance": distance,
            }
        )
    return chunks


def _parse_subqueries(raw: str, max_n: int) -> list[str]:
    """Pull one search query per line out of the model's decomposition response.

    Tolerates the numbering, bullets and quoting a small model tends to add
    despite being told not to. Anything that doesn't look like a query (blank
    lines, preamble sentences) is dropped.
    """
    subqueries = []
    for line in raw.splitlines():
        line = line.strip()
        line = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", line)  # strip list markers
        line = line.strip().strip('"').strip("'").strip()
        # Real queries are short; longer lines are almost always commentary.
        if not line or len(line) > 200:
            continue
        if line.endswith(":"):  # e.g. "Here are the queries:"
            continue
        subqueries.append(line)
        if len(subqueries) >= max_n:
            break
    return subqueries


def generate_subqueries(query: str, max_n: int = MAX_SUBQUERIES) -> list[str]:
    """Ask the model to split ``query`` into targeted retrieval queries.

    Returns an empty list if the model is unreachable or produces nothing
    usable, so callers can fall back to plain single-query retrieval.
    """
    messages = [
        {"role": "system", "content": DECOMPOSE_PROMPT.format(max_n=max_n)},
        {"role": "user", "content": query},
    ]
    try:
        raw = ollama_client.chat(messages, stream=False)
    except Exception:  # noqa: BLE001 — decomposition is best-effort
        return []
    return _parse_subqueries(raw or "", max_n)


def multi_retrieve(query: str, k: int = 4, max_n: int = MAX_SUBQUERIES) -> tuple[list[dict], list[str]]:
    """Retrieve for several targeted sub-queries and merge the results.

    A broad question ("summarize the ethical principles") embeds close to
    generic framing text, so similarity search fills the top ranks with
    boilerplate and buries the specific provisions. Splitting it into concrete
    sub-queries lets each one rank its own topic highly, which surfaces content
    a single query would miss without needing a much larger ``k``.

    The chunk budget stays near ``k``: it is shared across the sub-queries plus
    the original query, so context size (and latency) stays comparable.
    Returns ``(chunks, subqueries)``; ``subqueries`` is empty when decomposition
    failed and this fell back to a single query.
    """
    subqueries = generate_subqueries(query, max_n=max_n)
    # Always include the original query so nothing is lost if the split is poor.
    queries = [query] + subqueries
    per_query = max(MIN_CHUNKS_PER_SUBQUERY, k // len(queries))

    best_by_id: dict[str, dict] = {}
    for sub in queries:
        for chunk in retrieve(sub, k=per_query):
            existing = best_by_id.get(chunk["id"])
            if existing is None or chunk["distance"] < existing["distance"]:
                best_by_id[chunk["id"]] = chunk

    chunks = sorted(best_by_id.values(), key=lambda c: c["distance"])
    return chunks, subqueries


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


def _total_chars(messages: list[dict]) -> int:
    return sum(len(m["content"]) for m in messages)


def _trim_history(history: list[dict], available_chars: int) -> list[dict]:
    """Keep the most recent turns that fit in ``available_chars``.

    History is dropped oldest-first rather than cleared wholesale, so a long
    conversation degrades gradually instead of losing all its context at once.
    """
    kept: list[dict] = []
    used = 0
    for message in reversed(history):  # newest first
        cost = len(message["content"])
        if used + cost > available_chars:
            break
        kept.append(message)
        used += cost
    kept.reverse()
    return kept


def _num_ctx_for(messages: list[dict]) -> int:
    """Size the context window to fit ``messages`` plus room for the answer.

    Ollama's fixed default (2048 tokens) is fine for small ``top_k`` but starts
    silently truncating the retrieved context once more chunks are requested,
    which would otherwise defeat the point of raising ``top_k`` at all.
    """
    total_chars = sum(len(m["content"]) for m in messages)
    estimated_tokens = total_chars // CHARS_PER_TOKEN
    return max(DEFAULT_NUM_CTX, estimated_tokens + RESPONSE_MARGIN_TOKENS)


def answer(
    query: str,
    history: list[dict] | None = None,
    k: int = 4,
    multi_query: bool = False,
):
    """Retrieve context and stream an answer.

    With ``multi_query=True`` the question is first split into targeted
    sub-queries (one extra LLM call) so broad questions retrieve more evenly
    across topics; see :func:`multi_retrieve`. Narrow factual questions gain
    nothing from this and just pay the extra call.

    Returns ``(token_stream, chunks, meta)``. ``meta`` carries the generated
    ``subqueries`` (empty unless multi-query retrieval ran) and how many older
    conversation turns were ``dropped_turns`` to stay inside the context limit.
    """
    history = history or []
    if multi_query:
        chunks, subqueries = multi_retrieve(query, k=k)
    else:
        chunks, subqueries = retrieve(query, k=k), []

    # Retrieved context and the question itself are non-negotiable; whatever
    # budget is left over goes to conversation history, newest turns first.
    budget_chars = (MAX_CONTEXT_TOKENS - RESPONSE_MARGIN_TOKENS) * CHARS_PER_TOKEN
    fixed_chars = _total_chars(build_messages(query, chunks, []))
    kept_history = _trim_history(history, max(0, budget_chars - fixed_chars))

    messages = build_messages(query, chunks, kept_history)
    num_ctx = _num_ctx_for(messages)
    stream = ollama_client.chat(messages, stream=True, num_ctx=num_ctx)
    meta = {
        "subqueries": subqueries,
        "dropped_turns": len(history) - len(kept_history),
    }
    return stream, chunks, meta
