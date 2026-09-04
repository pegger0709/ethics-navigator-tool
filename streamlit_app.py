"""Ethics Navigator — a private, local RAG chatbot over your own documents."""

import uuid

import streamlit as st

from llm import ollama_client
from rag import corpus, embeddings, retriever, summaries

st.set_page_config(page_title="Ethics Navigator", page_icon="🧭", layout="wide")


@st.cache_resource(show_spinner="Preparing the model (first run downloads it)…")
def prepare() -> bool:
    """One-time startup: purge stale uploads, ensure models, index the corpus.

    Cached so it runs once per server process rather than on every rerun, which
    is exactly the granularity the purge wants: anything left in the session
    store belongs to a previous run of the app and must not survive into this
    one. Returns True on success; the caller surfaces failures (e.g.
    Ollama/Chroma unreachable).
    """
    embeddings.purge_session_store()
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
if "session_id" not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4().hex
session_id = st.session_state["session_id"]

# Closing a tab never reaches the server, so uploads from an abandoned session
# would otherwise sit in the store until the app restarts. Sweeping on every
# rerun bounds that to SESSION_TTL_SECONDS.
if backend_ready:
    embeddings.sweep_expired_uploads()

summaries_ready = backend_ready and summaries.summaries_available()


def end_session() -> None:
    """Drop every uploaded document and clear the conversation."""
    embeddings.purge_session_store()
    st.session_state["messages"] = []
    st.session_state["session_id"] = uuid.uuid4().hex

# --- Sidebar: document management + settings ---------------------------------
with st.sidebar:
    st.header("Your documents")
    st.caption("Everything stays on this machine — nothing is sent to the cloud.")

    jurisdictions = st.multiselect(
        "Where do you operate?",
        options=corpus.SELECTABLE_JURISDICTIONS,
        help="Global instruments (UN, UNESCO, OECD) always apply. Selecting a "
        "jurisdiction adds the legislation that binds you there.",
    )

    sources = embeddings.list_sources()
    if sources:
        st.subheader("In knowledge base")
        active = set(corpus.active_jurisdictions(jurisdictions))
        grouped = corpus.group_by_jurisdiction(sources)
        # Global first, then the selected jurisdictions, then anything inactive.
        order = [corpus.GLOBAL, *corpus.SELECTABLE_JURISDICTIONS]
        for group in [*order, *(g for g in grouped if g not in order)]:
            if group not in grouped:
                continue
            in_use = group in active
            st.caption(group if in_use else f"{group} — not selected")
            for source in grouped[group]:
                name = corpus.display_name(source)
                st.markdown(f"- {name}" if in_use else f"- :gray[{name}]")
    else:
        st.info("No documents indexed yet.")

    st.divider()

    st.subheader("This session's documents")
    st.caption(
        "Read into memory, indexed, and discarded — never written to disk. "
        "Removed automatically when you end the session, when the app "
        "restarts, or after a period of inactivity."
    )

    session_sources = embeddings.list_session_sources(session_id) if backend_ready else []
    if session_sources:
        for source in session_sources:
            st.markdown(f"- {corpus.display_name(source)}")

    with st.form("upload-form", clear_on_submit=True):
        uploaded = st.file_uploader(
            "Add documents for this session",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("Add to this session")
    if submitted and uploaded:
        with st.spinner("Indexing documents…"):
            embeddings.ingest_uploads(uploaded, session_id)
        st.rerun()

    if session_sources or st.session_state["messages"]:
        if st.button("🗑️ End session and delete documents"):
            end_session()
            st.rerun()

    st.divider()
    st.caption(
        "Each question is routed automatically: specific questions are answered "
        "from quoted excerpts, broad ones from pre-read document summaries."
    )
    if not summaries_ready:
        st.warning(
            "No document summaries built yet, so broad questions fall back to "
            "excerpts and will be patchy. Run `python -m rag.summaries`.",
            icon="⚠️",
        )

    with st.expander("Advanced"):
        mode_choice = st.selectbox(
            "Answer mode",
            options=["Automatic", *retriever.MODES],
            help="\n\n".join(
                f"**{name}** — {preset['hint']}"
                for name, preset in retriever.MODES.items()
            ),
        )
        override_k = st.checkbox("Override sources per answer")
        custom_k = st.slider(
            "Sources per answer",
            min_value=1,
            max_value=30,
            value=4,
            disabled=not override_k,
            help="How many excerpts or summary passages are retrieved.",
        )

    mode = None if mode_choice == "Automatic" else mode_choice
    top_k = custom_k if override_k else None

    if st.session_state["messages"]:
        if st.button("🧹 Clear conversation"):
            st.session_state["messages"] = []
            st.rerun()
        st.caption(
            "Older turns are dropped automatically only when the conversation "
            "no longer fits the model's context."
        )

def render_copy_button(text: str) -> None:
    """Offer ``text`` as a plain-text block so its hover icon copies it verbatim.

    st.code's built-in copy button is used rather than a custom component:
    it needs no JavaScript of our own and works inside Streamlit's sandboxed
    iframe, where clipboard access from custom HTML is unreliable.
    """
    with st.expander("📋 Copy response"):
        st.code(text, language=None, wrap_lines=True)


# --- Main: chat --------------------------------------------------------------
st.title("🧭 Ethics Navigator")
st.caption("Ask questions about your documents. Answers are grounded in them.")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_copy_button(message["content"])

if prompt := st.chat_input("Ask a question…", disabled=not backend_ready):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Pass prior turns (excluding the just-added question) as history.
        history = st.session_state["messages"][:-1]
        with st.spinner("Searching your documents…"):
            token_stream, chunks, meta = retriever.answer(
                prompt,
                history=history,
                mode=mode,
                k=top_k,
                jurisdictions=jurisdictions,
                session_id=session_id,
            )
        response = st.write_stream(token_stream)
        st.caption(f"Answered in **{meta['mode']}** mode.")
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
                    label = corpus.display_name(chunk["source"])
                    # Uploaded material is not an authority in the way an
                    # indexed instrument is; say which is which.
                    if chunk.get("uploaded"):
                        label += "  ·  _uploaded this session_"
                    st.markdown(f"**{label}**")
                    st.caption(chunk["text"][:500] + ("…" if len(chunk["text"]) > 500 else ""))
        render_copy_button(response)

    st.session_state["messages"].append({"role": "assistant", "content": response})
