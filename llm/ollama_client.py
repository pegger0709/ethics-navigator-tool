"""Ollama API wrapper.

All model names and the Ollama host live here as constants (overridable via
environment / .env) so they are configured in exactly one place — see CLAUDE.md.
"""

import os

from dotenv import load_dotenv
from ollama import Client

load_dotenv()  # idempotent; loads .env if present

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Answers user questions. This is the one model every user waits on, so it is
# picked for speed on CPU-only hardware rather than raw capability: measured
# against gpt-oss:20b on the eval suite, gemma3:4b runs the full case set in
# 40% of the time and fails nowhere gpt-oss:20b doesn't also fail (see
# report/ethics-navigator-report.qmd, "Trade-offs"). Letting users pick their
# own chat model was considered and rejected — it invites picking the largest
# one and then being frustrated by the latency, which is exactly the failure
# mode this default avoids.
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma3:4b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
# Routes each question to an answer mode. A two-way classification is easy, so
# this runs on a small model to keep the added per-question latency small.
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "llama3.2")
# Grades answers during evaluation only, never on the user-facing path, so
# there is no latency reason to hold back: use the largest model available.
# Deliberately a different family from CHAT_MODEL regardless of size — a model
# grading its own output shares its blind spots.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-oss:20b")
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
CHAT_SEED = int(os.getenv("CHAT_SEED", "42"))

# Models the app itself needs at runtime. JUDGE_MODEL is excluded on purpose —
# it is only used by evals/, and colleagues running the app should not have to
# download it.
RUNTIME_MODELS = (CHAT_MODEL, EMBED_MODEL, CLASSIFIER_MODEL)


def get_client() -> Client:
    """Return an Ollama client pointed at the configured host."""
    return Client(host=OLLAMA_HOST)


def _installed_models(client: Client) -> set[str]:
    """Return the set of model names Ollama already has locally.

    Normalises away the ``:tag`` suffix so ``tinyllama`` matches
    ``tinyllama:latest``.
    """
    names: set[str] = set()
    for model in client.list().models:
        # The ollama client exposes the name as ``.model``; fall back to dict
        # access for older client versions.
        name = getattr(model, "model", None) or model["name"]
        names.add(name)
        names.add(name.split(":", 1)[0])
    return names


def ensure_models(models: tuple[str, ...] = RUNTIME_MODELS, client: Client | None = None) -> None:
    """Pull any of ``models`` that are not already installed.

    This removes the need for a manual ``ollama pull`` step — the app calls it
    on startup so a fresh machine self-prepares. Defaults to the runtime models
    only; evals pass JUDGE_MODEL explicitly.
    """
    client = client or get_client()
    installed = _installed_models(client)
    for model in models:
        if model not in installed:
            # Stream the pull: a non-streaming pull holds one connection open
            # for the whole (multi-GB) download and gets dropped before it
            # finishes. Interrupted pulls resume where they left off.
            for _ in client.pull(model, stream=True):
                pass


def chat(
    messages: list[dict],
    stream: bool = True,
    num_ctx: int | None = None,
    model: str | None = None,
):
    """Send a chat conversation to Ollama.

    With ``stream=True`` (default) returns a generator of content token strings,
    suitable for ``st.write_stream``. With ``stream=False`` returns the full
    response string. ``num_ctx`` overrides Ollama's default context window (a
    fixed 2048 tokens regardless of what the model supports) — callers that
    stuff a lot of retrieved text into the prompt need to raise it or the extra
    context is silently truncated. ``model`` overrides CHAT_MODEL, for the
    classifier and judge which deliberately run on different models.
    """
    client = get_client()
    model = model or CHAT_MODEL

    options = {"temperature": CHAT_TEMPERATURE, "seed": CHAT_SEED}
    if num_ctx is not None:
        options["num_ctx"] = num_ctx

    if not stream:
        response = client.chat(model=model, messages=messages, options=options)
        return response.message.content

    def _token_stream():
        for chunk in client.chat(model=model, messages=messages, stream=True, options=options):
            token = chunk.message.content
            if token:
                yield token

    return _token_stream()
