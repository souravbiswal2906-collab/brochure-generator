"""
The only file in this project that talks to OpenAI.

Everything else asks this module for text and stays ignorant of which provider
is behind it. If you later switch to Anthropic, Gemini, or a local Ollama
model, this is the single file you rewrite.
"""

from __future__ import annotations

import json
from typing import Iterator

from openai import OpenAI

from . import config

# The client is created once, the first time it is needed, rather than at
# import time. That way importing this module never fails just because a key
# is missing, which keeps the tests runnable without one.
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        config.require_api_key()
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def _messages(system: str, user: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def complete(model: str, system: str, user: str) -> str:
    """Send one prompt, wait, return the whole reply as a string."""
    response = get_client().chat.completions.create(
        model=model,
        messages=_messages(system, user),
    )
    return response.choices[0].message.content or ""


def complete_json(model: str, system: str, user: str) -> dict:
    """
    Same as complete(), but ask the API to guarantee valid JSON.

    response_format is what makes this reliable. Without it you eventually get
    a reply wrapped in ```json fences that crashes json.loads at 2am.
    """
    response = get_client().chat.completions.create(
        model=model,
        messages=_messages(system, user),
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("  ! model returned something that was not valid JSON")
        return {}


def stream(model: str, system: str, user: str) -> Iterator[str]:
    """
    Yield the reply piece by piece as it arrives.

    Streaming does not make the request cheaper or faster overall, but the
    user sees words within a second instead of staring at nothing for twenty.
    """
    response = get_client().chat.completions.create(
        model=model,
        messages=_messages(system, user),
        stream=True,
    )
    for chunk in response:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece
