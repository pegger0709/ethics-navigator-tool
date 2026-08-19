"""Query logic: embed query -> retrieve chunks -> build prompt -> answer."""

import os
import re

from llm import ollama_client
from rag.corpus import active_jurisdictions, display_name
from rag.embeddings import KIND_CONTENT, KIND_SUMMARY, get_collection

DEFAULT_NUM_CTX = 2048  # Ollama's own default, used as a floor
RESPONSE_MARGIN_TOKENS = 1024  # headroom for the model's own answer
CHARS_PER_TOKEN = 4  # rough estimate, good enough for sizing the context window

# Hard ceiling on prompt size. The model itself allows far more, but every
# extra token costs CPU time, so conversation history is trimmed to fit this
# rather than being allowed to grow without bound.
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "8192"))

# The two question types need different sources, not different amounts of the
# same source. Specific questions are answered from verbatim excerpts, where
# k=4 was measured to retrieve every known-good passage. Broad questions are
# answered from pre-built digests (rag/summaries.py), because similarity search
# over excerpts finds 0 of 3 known-relevant passages for them at any practical k.
MODE_QA = "Question answering"
MODE_BROAD = "Broad principles"

MODES: dict[str, dict] = {
    MODE_QA: {
        "k": 4,
        "kind": KIND_CONTENT,
        "multi_query": False,
        "hint": "Specific facts, quoted from the documents.",
    },
    MODE_BROAD: {
        "k": 12,
        "kind": KIND_SUMMARY,
        "multi_query": False,
        "hint": "Overviews built from pre-read summaries of each document.",
    },
}
DEFAULT_MODE = MODE_QA

CLASSIFY_PROMPT = (
    "Classify the user's question into exactly one category.\n\n"
    "SPECIFIC — asks for a particular fact, definition, or provision that "
    "would be stated in one place.\n"
    "BROAD — asks to summarize, list, or give an overview of a whole topic "
    "across a document.\n\n"
    "Reply with exactly one word: SPECIFIC or BROAD.\n\n"
    "QUESTION: {query}"
)

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


def _build_where(kind: str | None, jurisdictions: list[str] | None) -> dict | None:
    """Assemble a Chroma metadata filter from the active kind and jurisdictions."""
    clauses: list[dict] = []
    if kind:
        clauses.append({"kind": kind})
    if jurisdictions is not None:
        clauses.append({"jurisdiction": {"$in": list(jurisdictions)}})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def retrieve(
    query: str,
    k: int = 4,
    kind: str | None = KIND_CONTENT,
    jurisdictions: list[str] | None = None,
) -> list[dict]:
    """Return the top-``k`` chunks for ``query`` as ``{id, text, source, distance}`` dicts.

    ``kind`` selects which pool to search: verbatim excerpts (the default) for
    specific questions, or pre-built digests for broad ones. Passing ``None``
    searches both. ``jurisdictions`` limits results to documents that apply
    where the user operates; ``None`` means no jurisdiction filter.
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_texts=[query],
        n_results=min(k, count),
        where=_build_where(kind, jurisdictions),
    )
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


def classify_mode(query: str) -> str:
    """Pick the answer mode for ``query`` with one small-model call.

    Runs on CLASSIFIER_MODEL rather than the workhorse: a two-way choice is an
    easy task, so this adds a fraction of a generation's latency. Any
    unrecognised reply falls back to question answering, the cheaper mode.
    """
    messages = [{"role": "user", "content": CLASSIFY_PROMPT.format(query=query)}]
    try:
        raw = ollama_client.chat(
            messages, stream=False, model=ollama_client.CLASSIFIER_MODEL
        ) or ""
    except Exception:  # noqa: BLE001 — routing is best-effort
        return DEFAULT_MODE
    return MODE_BROAD if "BROAD" in raw.strip().upper() else MODE_QA


def retrieve_for(
    query: str,
    k: int,
    multi_query: bool = False,
    kind: str | None = KIND_CONTENT,
    jurisdictions: list[str] | None = None,
) -> tuple[list[dict], list[str]]:
    """Retrieve using the configured strategy. Returns ``(chunks, subqueries)``.

    The single entry point both :func:`answer` and the retrieval eval go
    through, so what is measured is exactly what production runs.
    """
    if multi_query:
        return multi_retrieve(query, k=k)
    return retrieve(query, k=k, kind=kind, jurisdictions=jurisdictions), []


def build_messages(query: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    """Assemble the message list: system prompt + context, prior turns, query."""
    if chunks:
        # Cite documents by title: the model quotes whatever label it is given,
        # and "UNESCO_397812eng.pdf" is meaningless to a reader.
        context = "\n\n".join(
            f"[Source: {display_name(c['source'])}]\n{c['text']}" for c in chunks
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
    mode: str | None = None,
    k: int | None = None,
    multi_query: bool = False,
    jurisdictions: list[str] | None = None,
):
    """Retrieve context and stream an answer.

    ``mode`` selects which pool to answer from; when omitted it is chosen
    automatically by :func:`classify_mode`. ``jurisdictions`` are the
    place-specific regimes the user operates under; global instruments are
    always included alongside them. ``k`` and ``multi_query`` override the
    mode's defaults for experiments.

    Returns ``(token_stream, chunks, meta)``. ``meta`` reports the ``mode``
    actually used — the UI shows it, so an automatic misroute is visible rather
    than an unexplained bad answer — plus any generated ``subqueries`` and how
    many older conversation turns were ``dropped_turns`` to fit the context.
    """
    history = history or []
    mode = mode or classify_mode(query)
    preset = MODES.get(mode, MODES[DEFAULT_MODE])
    k = preset["k"] if k is None else k
    allowed = active_jurisdictions(jurisdictions)

    chunks, subqueries = retrieve_for(
        query,
        k=k,
        multi_query=multi_query,
        kind=preset["kind"],
        jurisdictions=allowed,
    )
    # A broad question before digests are built would otherwise silently answer
    # from nothing; fall back to excerpts rather than returning an empty context.
    if not chunks and preset["kind"] == KIND_SUMMARY:
        chunks, subqueries = retrieve_for(
            query, k=k, kind=KIND_CONTENT, jurisdictions=allowed
        )
        mode = f"{mode} (no summaries built; used excerpts)"

    # Retrieved context and the question itself are non-negotiable; whatever
    # budget is left over goes to conversation history, newest turns first.
    budget_chars = (MAX_CONTEXT_TOKENS - RESPONSE_MARGIN_TOKENS) * CHARS_PER_TOKEN
    fixed_chars = _total_chars(build_messages(query, chunks, []))
    kept_history = _trim_history(history, max(0, budget_chars - fixed_chars))

    messages = build_messages(query, chunks, kept_history)
    num_ctx = _num_ctx_for(messages)
    stream = ollama_client.chat(messages, stream=True, num_ctx=num_ctx)
    meta = {
        "mode": mode,
        "subqueries": subqueries,
        "dropped_turns": len(history) - len(kept_history),
    }
    return stream, chunks, meta
