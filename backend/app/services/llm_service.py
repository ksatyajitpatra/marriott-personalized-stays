"""LiteLLM client — wraps the TIP.AI proxy with a mock fallback.

Usage:
    text = await litellm_chat([
        {"role": "system", "content": "You are a concierge."},
        {"role": "user",   "content": "Welcome the guest."},
    ])

When `settings.use_mock_llm` is true (default), this raises so callers can
fall back to seeded fixtures. When false, a real HTTPS POST is issued to
the LiteLLM proxy.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMConfigError(RuntimeError):
    """Raised when live LLM calls are requested without proper config."""


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM call fails at runtime (network, 5xx, etc.)."""


def _validate_live_config() -> None:
    """Ensure we have everything needed for a real LLM call."""
    if not settings.litellm_base_url:
        raise LLMConfigError("LITELLM_BASE_URL is not set")
    if not settings.litellm_api_key:
        raise LLMConfigError("LITELLM_API_KEY is not set")
    if not settings.litellm_model:
        raise LLMConfigError("LITELLM_MODEL is not set")


async def litellm_chat(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 800,
    response_format: dict[str, Any] | None = None,
) -> str:
    """Call the LiteLLM `/v1/chat/completions` endpoint and return the text.

    Args:
        messages: OpenAI-style chat messages.
        max_tokens: Max tokens to generate.
        response_format: Optional response_format hint (e.g. JSON mode).

    Returns:
        The assistant's reply content as a string.

    Raises:
        LLMConfigError: If `use_mock_llm` is true or required env is missing.
        LLMUnavailableError: If the upstream call fails.
    """
    if settings.use_mock_llm:
        raise LLMConfigError("Live LLM disabled (USE_MOCK_LLM=true)")

    _validate_live_config()

    payload: dict[str, Any] = {
        "model": settings.litellm_model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    temp = settings.litellm_temperature_value
    if temp is not None:
        payload["temperature"] = temp
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {settings.litellm_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.litellm_base_url.rstrip('/')}/v1/chat/completions"

    # `verify=False` matches the `test_litellm_models.py` smoke script — the
    # CloudFront proxy uses a cert chain that some macOS Python builds reject.
    try:
        async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("LiteLLM request failed")
        raise LLMUnavailableError(str(exc)) from exc

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMUnavailableError(f"Unexpected LLM response shape: {data}") from exc


def parse_llm_json(raw: str) -> Any:
    """Parse JSON from an LLM reply, stripping optional markdown fences."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1)
        text = re.sub(r"\s*```$", "", text, count=1)
    return json.loads(text.strip())


async def litellm_chat_with_tools(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]],
    max_tokens: int = 1200,
    tool_choice: str | dict[str, Any] = "auto",
) -> dict[str, Any]:
    """Call the LiteLLM proxy with OpenAI-style tool definitions.

    Args:
        messages: OpenAI-style chat messages (may include role=tool entries).
        tools: List of OpenAI tool schemas (``{"type": "function", "function": {...}}``).
        max_tokens: Max tokens to generate.
        tool_choice: ``"auto"``, ``"none"``, or a forced tool selector.

    Returns:
        The full assistant ``message`` dict, e.g.
        ``{"role": "assistant", "content": "...", "tool_calls": [...]}``.

    Raises:
        LLMConfigError: When ``USE_MOCK_LLM`` is true or required env is missing.
        LLMUnavailableError: When the upstream call fails or returns a bad shape.
    """
    if settings.use_mock_llm:
        raise LLMConfigError("Live LLM disabled (USE_MOCK_LLM=true)")

    _validate_live_config()

    payload: dict[str, Any] = {
        "model": settings.litellm_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "tools": tools,
        "tool_choice": tool_choice,
    }
    temp = settings.litellm_temperature_value
    if temp is not None:
        payload["temperature"] = temp

    headers = {
        "Authorization": f"Bearer {settings.litellm_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.litellm_base_url.rstrip('/')}/v1/chat/completions"

    try:
        async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("LiteLLM tool-calling request failed")
        raise LLMUnavailableError(str(exc)) from exc

    try:
        return data["choices"][0]["message"]
    except (KeyError, IndexError) as exc:
        raise LLMUnavailableError(f"Unexpected LLM response shape: {data}") from exc
