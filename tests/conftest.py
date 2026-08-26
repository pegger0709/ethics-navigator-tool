"""Shared fixtures for the RAG pipeline integration tests.

These tests exercise the real pipeline (Chroma + Ollama), so they require a
running Ollama service. Each subset of test documents gets its own temporary
Chroma store, and every (subset, prompt) combination is asked twice and cached
so the determinism, no-hallucination, and grounded-answer tests share results
instead of re-calling the model.
"""

import os
import shutil
import tempfile

import pytest

from llm import ollama_client
from rag import embeddings, retriever

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

D1 = "UN_declaration_HumanRights.pdf"
D2 = "chocolate-cake-A4.pdf"
P1 = (
    "Is the ability to occasionally take a reasonable amount of time off work "
    "a right for all or a privilege for some?"
)
P2 = "How long should I bake a chocolate cake?"

SUBSETS = [(), (D1,), (D2,), (D1, D2)]

# The suite checks pipeline behaviour — determinism, grounding, refusal — not
# the quality of any one model. This once pinned a small model because the app
# default was llama3.1:8b, which took ~12 hours to test against; now that the
# default is itself small and fast, the pin tracks it instead, so the tests
# exercise what actually ships and a dev machine needs one fewer model. The
# override remains for bisecting a behaviour change across models.
TEST_CHAT_MODEL = os.getenv("TEST_CHAT_MODEL", ollama_client.CHAT_MODEL)


def subset_id(subset: tuple[str, ...]) -> str:
    """Readable pytest parameter id for a document subset."""
    names = {D1: "D1", D2: "D2"}
    return "{" + ",".join(names[doc] for doc in subset) + "}"


@pytest.fixture(scope="session")
def fast_chat_model():
    """Pin the suite to ``TEST_CHAT_MODEL`` instead of the app's default."""
    patcher = pytest.MonkeyPatch()
    patcher.setattr(ollama_client, "CHAT_MODEL", TEST_CHAT_MODEL)
    yield TEST_CHAT_MODEL
    patcher.undo()


@pytest.fixture(scope="session")
def ollama_available(fast_chat_model):
    """Skip the whole suite when Ollama is unreachable."""
    try:
        ollama_client.ensure_models()
    except Exception as exc:
        pytest.skip(f"Ollama is not reachable at {ollama_client.OLLAMA_HOST}: {exc}")


@pytest.fixture(scope="session")
def get_responses(ollama_available):
    """Return a ``(subset, prompt) -> (response_1, response_2)`` accessor.

    Each subset is ingested once into its own temporary Chroma store, and each
    prompt is asked twice against it (to verify determinism). Results are
    cached for the whole session.

    Temp stores come from ``tempfile.mkdtemp`` rather than ``tmp_path_factory``
    because pytest's shared ``pytest-of-<user>`` temp root can have broken ACLs
    on Windows (PermissionError on scandir).
    """
    patcher = pytest.MonkeyPatch()
    patcher.delenv("CHROMA_HOST", raising=False)
    stores: dict[tuple[str, ...], str] = {}
    responses: dict[tuple[tuple[str, ...], str], tuple[str, str]] = {}

    def ensure_store(subset: tuple[str, ...]) -> str:
        if subset not in stores:
            persist_dir = tempfile.mkdtemp(prefix="ethics_navigator_test_chroma_")
            patcher.setattr(embeddings, "CHROMA_PERSIST_DIR", persist_dir)
            collection = embeddings.get_collection()
            for filename in subset:
                with open(os.path.join(DOCUMENTS_DIR, filename), "rb") as handle:
                    text = embeddings.extract_text(filename, handle.read())
                embeddings._add_document(collection, text, filename)
            stores[subset] = persist_dir
        return stores[subset]

    def ask_twice(subset: tuple[str, ...], prompt: str) -> tuple[str, str]:
        key = (subset, prompt)
        if key not in responses:
            patcher.setattr(embeddings, "CHROMA_PERSIST_DIR", ensure_store(subset))
            first = "".join(retriever.answer(prompt)[0])
            second = "".join(retriever.answer(prompt)[0])
            responses[key] = (first, second)
        return responses[key]

    yield ask_twice
    patcher.undo()
    for persist_dir in stores.values():
        # ignore_errors: Chroma may still hold SQLite file locks on Windows
        shutil.rmtree(persist_dir, ignore_errors=True)
