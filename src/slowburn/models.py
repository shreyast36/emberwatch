"""Unified async interface to Claude, GPT, Gemini.

Owner: Binjie. See ROLES.md.

Each implementation:
- accepts a `model_name` so we can swap Sonnet/Opus/Haiku, GPT-5/Nano, etc.
- handles rate limits with exponential backoff
- exposes a single `async def complete(messages, max_tokens) -> str`
"""

from typing import Protocol


class Model(Protocol):
    model_name: str
    provider: str

    async def complete(self, messages: list[dict], max_tokens: int) -> str: ...


class ClaudeModel:
    """Default model_name: 'claude-sonnet-4-6'. Uses the anthropic SDK."""

    provider = "anthropic"

    def __init__(self, model_name: str = "claude-sonnet-4-7") -> None:
        raise NotImplementedError("TODO(binjie): implement ClaudeModel.complete with backoff")

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        raise NotImplementedError


class OpenAIModel:
    """Uses the openai SDK."""

    provider = "openai"

    def __init__(self, model_name: str = "gpt-5") -> None:
        raise NotImplementedError("TODO(binjie): implement OpenAIModel.complete with backoff")

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        raise NotImplementedError


class GeminiModel:
    """Uses google-genai."""

    provider = "google"

    def __init__(self, model_name: str = "gemini-2.5-pro") -> None:
        raise NotImplementedError("TODO(binjie): implement GeminiModel.complete with backoff")

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        raise NotImplementedError


class WaferModel:
    """Uses Wafer AI for GLM and Qwen models."""
    
    provider = "wafer"

    def __init__(self, model_name: str = "glm-4") -> None:
        raise NotImplementedError("TODO(binjie): implement WaferModel.complete with backoff")

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        raise NotImplementedError
