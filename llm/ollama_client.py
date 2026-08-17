"""Ollama API wrapper.

All model names and the Ollama host live here as constants (overridable via
environment / .env) so they are configured in exactly one place — see CLAUDE.md.
"""

import os

from dotenv import load_dotenv
from ollama import Client

load_dotenv()  # idempotent; loads .env if present

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
CHAT_SEED = int(os.getenv("CHAT_SEED", "42"))


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


def ensure_models(client: Client | None = None) -> None:
    """Pull CHAT_MODEL and EMBED_MODEL if they are not already installed.

    This removes the need for a manual ``ollama pull`` step — the app calls it
    on startup so a fresh machine self-prepares.
    """
    client = client or get_client()
    installed = _installed_models(client)
    for model in (CHAT_MODEL, EMBED_MODEL):
        if model not in installed:
            client.pull(model)


def chat(messages: list[dict], stream: bool = True, num_ctx: int | None = None):
    """Send a chat conversation to Ollama.

    With ``stream=True`` (default) returns a generator of content token strings,
    suitable for ``st.write_stream``. With ``stream=False`` returns the full
    response string. ``num_ctx`` overrides Ollama's default context window (a
    fixed 2048 tokens regardless of what the model supports) — callers that
    stuff a lot of retrieved text into the prompt need to raise it or the extra
    context is silently truncated.
    """
    client = get_client()

    options = {"temperature": CHAT_TEMPERATURE, "seed": CHAT_SEED}
    if num_ctx is not None:
        options["num_ctx"] = num_ctx

    if not stream:
        response = client.chat(model=CHAT_MODEL, messages=messages, options=options)
        return response.message.content

    def _token_stream():
        for chunk in client.chat(model=CHAT_MODEL, messages=messages, stream=True, options=options):
            token = chunk.message.content
            if token:
                yield token

    return _token_stream()
