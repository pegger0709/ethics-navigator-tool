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

# Ingest documents into Chroma (run after adding files to data/documents/)
python -m rag.embeddings

# Add a dependency: edit requirements.txt by hand, then reinstall
# Do NOT use `pip freeze` — it captures transitive deps and pollutes the file

# Docker: build and run the full stack (Streamlit + Chroma + Ollama)
docker compose up --build

# Docker: tear down
docker compose down
```

## Architecture

```
ethics-navigator-tool/
├── streamlit_app.py       # Single-page Streamlit UI and app entrypoint
├── requirements.txt
├── .streamlit/
│   └── config.toml        # Streamlit theme/config (do not store secrets here)
├── rag/
│   ├── embeddings.py      # Chroma collection setup and document ingestion
│   └── retriever.py       # Query logic: embed query → retrieve chunks → prompt
├── llm/
│   └── ollama_client.py   # Ollama API wrapper (model name configurable)
├── data/
│   └── documents/         # Source documents for ingestion into Chroma
├── chroma_db/             # Persisted Chroma vector store (local, not committed)
├── Dockerfile             # TODO: Streamlit app container (not yet written)
└── docker-compose.yml     # TODO: multi-container setup: streamlit + chroma + ollama (not yet written)
```

## Invariants

- Ollama runs as a local service (default: `http://localhost:11434`); model name is a constant in `llm/ollama_client.py` — default model is `tinyllama`
- Chroma uses a persistent local client pointed at `chroma_db/`; do not use the in-memory client
- Conversation history is managed in `st.session_state`; do not store it in Chroma

## Conventions

- Single `requirements.txt`; no pyproject.toml or setup.py needed
- All Streamlit UI code stays in `streamlit_app.py`; business logic goes in `rag/` or `llm/`
- Prefer simple functions over classes unless state is genuinely needed
- Use `st.chat_message` and `st.chat_input` for the chat interface (not custom components)

## Off-limits

- Do not commit `.venv/`
- Do not store secrets or API keys in `.streamlit/config.toml`; use `.streamlit/secrets.toml` and keep it in .gitignore