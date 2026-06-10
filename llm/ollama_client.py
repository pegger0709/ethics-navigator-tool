"""Ollama API wrapper.

All model names and the Ollama host live here as constants (overridable via
environment / .env) so they are configured in exactly one place — see CLAUDE.md.
"""

import os

from dotenv import load_dotenv
from ollama import Client

load_dotenv()  # idempotent; loads .env if present

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "tinyllama")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


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


def chat(messages: list[dict], stream: bool = True):
    """Send a chat conversation to Ollama.

    With ``stream=True`` (default) returns a generator of content token strings,
    suitable for ``st.write_stream``. With ``stream=False`` returns the full
    response string.
    """
    client = get_client()

    if not stream:
        response = client.chat(model=CHAT_MODEL, messages=messages)
        return response.message.content

    def _token_stream():
        for chunk in client.chat(model=CHAT_MODEL, messages=messages, stream=True):
            token = chunk.message.content
            if token:
                yield token

    return _token_stream()
