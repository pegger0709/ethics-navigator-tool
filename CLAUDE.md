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

# Ingest documents into Chroma (the app also auto-ingests an empty collection on startup)
python -m rag.embeddings

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
│   ├── embeddings.py      # Chroma client + collection setup + document ingestion
│   └── retriever.py       # Query logic: retrieve chunks → build prompt → answer
├── llm/
│   └── ollama_client.py   # Ollama API wrapper; model-name constants + ensure_models()
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

- Ollama runs as a local service; host and model names are constants in `llm/ollama_client.py` (env-overridable). Default chat model `llama3.2`, embed model `nomic-embed-text`. All model names live here only.
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