# Ethics Navigator

A single-page RAG chatbot built with Streamlit, Chroma, and Ollama (local LLM).

## Requirements

- Python 3.13
- [Ollama](https://ollama.com) running locally (default: `http://localhost:11434`)

## Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# Ingest documents into Chroma (the app also syncs new/removed documents on startup)
python -m rag.embeddings

# Build per-document digests, which broad questions are answered from.
# Expensive (tens of minutes to hours of CPU inference per document) and NOT run
# at startup, so build one document at a time as capacity allows.
python -m rag.summaries --source UNESCO_397812eng.md

# Evaluate: retrieval stage only (seconds, no LLM) — the fast loop for tuning k
python -m evals.retrieval

# Evaluate: full answer quality against the real corpus (slow, deliberate)
python -m evals.run

# Run the test suite (integration tests: requires Ollama running; exercises the real model).
# Runs against the app's own chat model (override with TEST_CHAT_MODEL) — the tests
# check pipeline behaviour, not model quality.
pytest

# Add a dependency: edit requirements.txt by hand, then reinstall
# Do NOT use `pip freeze` — it captures transitive deps and pollutes the file

# Docker: build and run the full stack (Streamlit + Chroma + Ollama)
# Models are pulled automatically on first startup via ensure_models() — no manual `ollama pull`
docker compose up --build

# Docker: tear down (add -v to also clear model + vector-store volumes)
docker compose down
```

## Architecture

```
ethics-navigator-tool/
├── streamlit_app.py       # Single-page Streamlit UI and app entrypoint
├── requirements.txt
├── .env.example           # Documented env vars; copy to .env (gitignored) to override
├── .streamlit/
│   └── config.toml        # Streamlit theme/config (do not store secrets here)
├── rag/
│   ├── corpus.py          # Document registry: display names + jurisdictions
│   ├── embeddings.py      # Chroma client + collection setup + document ingestion
│   ├── retriever.py       # Query logic: classify mode → retrieve → prompt → answer
│   └── summaries.py       # Builds per-document digests for broad questions
├── llm/
│   └── ollama_client.py   # Ollama API wrapper; model-name constants + ensure_models()
├── evals/                 # Quality measurement (slow, deliberate; not pytest)
│   ├── dataset.py         # Gold cases, shared with tests/ via needs_docs
│   ├── graders.py         # refusal / contains / LLM-as-judge
│   ├── retrieval.py       # Retrieval-stage recall + source balance
│   └── run.py             # Full scorecard
├── data/
│   └── documents/         # Source documents for ingestion into Chroma
├── chroma_db/             # Persisted Chroma vector store (local mode only)
├── docs/                  # Vendored API reference for Chroma/Ollama/Streamlit/Docker
├── Dockerfile             # Streamlit app container
└── docker-compose.yml     # Streamlit + Chroma + Ollama stack
```

## Reference docs

`docs/` holds the authoritative API reference for Chroma, Ollama, Streamlit, and Docker. Each has a short index (`<tool>-reference.md`, lists topics + URLs) and a full dump (`<tool>-reference-full.md`, actual content), plus `ollama-api.md`. Consult these for API signatures rather than relying on memory — these tools change fast.

## Invariants

- Ollama runs as a local service; host and model names are constants in `llm/ollama_client.py` (env-overridable). Chat `gemma3:4b` (chosen for speed on CPU — see report/), embed `nomic-embed-text`, classifier defaults to the chat model (one fewer download; a two-way routing call does not need its own model), judge `gpt-oss:20b` (evals only — no latency constraint off the user-facing path, so use the largest model). All model names live here only. Runtime needs exactly two models — keep it that way: every extra one is multi-GB on a colleague's laptop.
- **Never wipe the Chroma collection to change metadata.** Digest chunks (`kind="summary"`) live in the same collection as content chunks and cost hours of CPU inference to rebuild, while `ingest()` only restores content. Use `collection.update(ids=..., metadatas=...)` to migrate metadata in place.
- **One indexed file per document.** A document's identity is its filename *stem* (`rag/corpus.py`), so `EU_GDPR.md` and `EU_GDPR.pdf` are the same document, not two. `resolve_sources()` picks one file per stem — markdown first, then `.txt`, then `.pdf` — because the converted markdown carries the headings chunking splits on, while the PDF is kept as the unaltered original for provenance. Never iterate `DOCUMENTS_DIR` directly to decide what to index: holding a document in two formats put a second near-identical copy of every chunk into the collection, which halves the number of *distinct* passages a given `k` can reach and lets one document outvote the corpus purely because it is stored twice.
- **Publisher/administrative boilerplate is stripped before chunking, not filtered at query time.** `strip_boilerplate()` in `rag/embeddings.py` drops table-of-contents entries and named sections (audited per document — see the function's docstring) whose text matches a known publisher/rights phrase, because a query that names the document (e.g. "the OECD document") matches its own title page and citation instructions more strongly than its provisions. The stoplist is intentionally conservative: a heading is only removed unconditionally if it is a bare table of contents; anything else requires its body to match a rights/citation phrase, so a document with its own legitimate section sharing one of these titles is not silently deleted. This does not fully resolve retrieval for every query that names a document — see `oecd-due-regard` in `evals/dataset.py`, which still fails because the OECD Recommendation's own operative preamble ("HAVING REGARD to ...") is a strong lexical match for "due regard" and is not boilerplate, so it is deliberately left alone.
- **Two collections, and uploads never enter the corpus one.** `ethics_docs` is the fixed reference corpus; `ethics_session` holds documents uploaded at runtime. Uploaded material is confidential partner content, so it is held in memory only long enough to chunk and embed (never written to `data/documents/`, which would survive every purge and be re-indexed into the corpus on the next startup), and it is removed by dropping the whole collection — on app start, on an age sweep (`SESSION_TTL_SECONDS`), and on an explicit end-session action. Keep purging a collection-level delete: a filter can be wrong, a `delete_collection` cannot reach corpus or digest chunks.
- Uploaded chunks are searched alongside the corpus but scoped differently: no jurisdiction filter (the user's own material is always in scope) and always retrieved as `content` (a session-lived document never gets a digest built).
- Chunks carry `source`, `kind` (`content` | `summary`) and `jurisdiction`. Specific questions retrieve `content`, broad ones retrieve `summary`; retrieval is always filtered to the global instruments plus the user's selected jurisdictions (`rag/corpus.py`).
- Chroma client is env-driven (`rag/embeddings.py`): `PersistentClient(path=chroma_db/)` locally, `HttpClient(host, port)` when `CHROMA_HOST` is set (the Docker stack). Never use the in-memory client.
- Embedding goes through Chroma's `OllamaEmbeddingFunction` attached to the collection, so ingestion and query embedding share one path; only chat goes through `ollama_client.py`.
- Conversation history is managed in `st.session_state`; do not store it in Chroma.
- Config comes from `.env` (loaded via `python-dotenv`; read automatically by Docker Compose). The real `.env` stays gitignored; document new vars in `.env.example`.

## Conventions

- Single `requirements.txt`; no pyproject.toml or setup.py needed
- All Streamlit UI code stays in `streamlit_app.py`; business logic goes in `rag/` or `llm/`
- Prefer simple functions over classes unless state is genuinely needed
- Use `st.chat_message` and `st.chat_input` for the chat interface (not custom components)

## Off-limits

- Do not commit `.venv/`
- Do not store secrets or API keys in `.streamlit/config.toml`; use `.streamlit/secrets.toml` and keep it in .gitignore