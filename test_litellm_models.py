"""LiteLLM proxy helper — list models and call a model.

Usage:
    export LITELLM_BASE_URL=https://d1t4hkdc2i746c.cloudfront.net
    export LITELLM_API_KEY=sk-<your-api-key>
    python test_litellm_models.py
"""

from __future__ import annotations

import os
import httpx

BASE_URL = os.environ.get("LITELLM_BASE_URL", "https://d1t4hkdc2i746c.cloudfront.net").rstrip("/")
API_KEY  = os.environ.get("LITELLM_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def get_models() -> list[str]:
    """Return all model IDs available on the proxy."""
    r = httpx.get(f"{BASE_URL}/v1/models", headers=HEADERS, verify=False)
    r.raise_for_status()
    return [m["id"] for m in r.json().get("data", [])]


def call_model(
    model: str,
    user_message: str,
    system: str = "You are a helpful assistant.",
    temperature: float | None = 0.7,
) -> str:
    """Send a chat completion request and return the assistant reply.

    Args:
        model: Model ID from get_models(), e.g. 'us.anthropic.claude-sonnet-4-6'.
        user_message: The user turn content.
        system: Optional system prompt.
        temperature: Sampling temperature. Set to None for models that don't support it
            (e.g. us.anthropic.claude-opus-4-7 on Bedrock).

    Returns:
        The assistant's reply text.
    """
    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_message},
        ],
        "max_tokens": 500,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    r = httpx.post(f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json=payload, verify=False, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "choices" not in data:
        raise ValueError(f"Unexpected response: {data}")
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("=== Available models ===")
    for m in get_models():
        print(" -", m)

    print("\n=== Claude Sonnet 4.6 ===")
    print(call_model("us.anthropic.claude-sonnet-4-6", "Explain quantum computing in simple terms."))

    print("\n=== Claude Opus 4.7 ===")
    print(call_model("us.anthropic.claude-opus-4-7", "Explain quantum computing in simple terms.", temperature=None))
