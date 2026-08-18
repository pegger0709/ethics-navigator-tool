"""Ethics Navigator — a private, local RAG chatbot over your own documents."""

import streamlit as st

from llm import ollama_client
from rag import embeddings, retriever

st.set_page_config(page_title="Ethics Navigator", page_icon="🧭", layout="wide")


@st.cache_resource(show_spinner="Preparing the model (first run downloads it)…")
def prepare() -> bool:
    """One-time startup: ensure models are present and index any existing docs.

    Cached so it runs once per session rather than on every rerun. Returns True
    on success; the caller surfaces failures (e.g. Ollama/Chroma unreachable).
    """
    ollama_client.ensure_models()
    embeddings.ingest()
    return True


try:
    prepare()
    backend_ready = True
except Exception as exc:  # noqa: BLE001 — surface any startup failure to the user
    backend_ready = False
    st.error(
        "Couldn't reach the AI backend. If you're running locally, make sure "
        f"Ollama is running. Details: {exc}"
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Sidebar: document management + settings ---------------------------------
with st.sidebar:
    st.header("Your documents")
    st.caption("Everything stays on this machine — nothing is sent to the cloud.")

    sources = embeddings.list_sources()
    if sources:
        st.subheader("In knowledge base")
        for source in sources:
            st.markdown(f"- {source}")
    else:
        st.info("No documents indexed yet.")

    st.divider()

    with st.form("upload-form", clear_on_submit=True):
        uploaded = st.file_uploader(
            "Add documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("Add to knowledge base")
    if submitted and uploaded:
        with st.spinner("Indexing documents…"):
            added = embeddings.ingest_uploads(uploaded)
        st.rerun()

    st.divider()
    st.subheader("Answer mode")
    mode = st.radio(
        "Answer mode",
        options=list(retriever.MODES),
        index=list(retriever.MODES).index(retriever.DEFAULT_MODE),
        label_visibility="collapsed",
        captions=[m["hint"] for m in retriever.MODES.values()],
    )
    preset = retriever.MODES[mode]

    with st.expander("Advanced"):
        st.caption("Overrides the mode above.")
        top_k = st.slider(
            "Sources per answer",
            min_value=1,
            max_value=30,
            value=preset["k"],
            help="How many document excerpts are retrieved to answer from. "
            "More covers broad questions better but is slower on CPU.",
        )
        multi_query = st.toggle(
            "Split question into several searches",
            value=preset["multi_query"],
            help="Rewrites your question as a few targeted searches before "
            "answering, so broad questions cover more of the documents. Costs "
            "one extra model call; narrow factual questions don't need it.",
        )

    if st.session_state["messages"]:
        if st.button("🧹 Clear conversation"):
            st.session_state["messages"] = []
            st.rerun()
        st.caption(
            "Older turns are dropped automatically only when the conversation "
            "no longer fits the model's context."
        )

# --- Main: chat --------------------------------------------------------------
st.title("🧭 Ethics Navigator")
st.caption("Ask questions about your documents. Answers are grounded in them.")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question…", disabled=not backend_ready):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Pass prior turns (excluding the just-added question) as history.
        history = st.session_state["messages"][:-1]
        with st.spinner("Searching your documents…"):
            token_stream, chunks, meta = retriever.answer(
                prompt, history=history, k=top_k, multi_query=multi_query
            )
        response = st.write_stream(token_stream)
        if meta["dropped_turns"]:
            st.caption(
                f"⚠️ Dropped the {meta['dropped_turns']} oldest conversation "
                "turn(s) to stay within the context limit."
            )
        if meta["subqueries"]:
            with st.expander(f"Search queries ({len(meta['subqueries'])})"):
                for subquery in meta["subqueries"]:
                    st.markdown(f"- {subquery}")
        if chunks:
            with st.expander(f"Sources ({len(chunks)})"):
                for chunk in chunks:
                    st.markdown(f"**{chunk['source']}**")
                    st.caption(chunk["text"][:500] + ("…" if len(chunk["text"]) > 500 else ""))

    st.session_state["messages"].append({"role": "assistant", "content": response})
