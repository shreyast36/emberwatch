"""Unified async interface to Claude, GPT, Gemini.

Owner: Binjie. See ROLES.md.

Each implementation:
- accepts a `model_name` so we can swap Sonnet/Opus/Haiku, GPT-5/Nano, etc.
- handles rate limits with exponential backoff
- exposes a single `async def complete(messages, max_tokens) -> str`
"""

import asyncio
import os
import random
from typing import Protocol

import anthropic
import google.genai
import google.genai.errors
import google.genai.types
import openai


async def _with_backoff(fn, retryable_exceptions, max_attempts=6, base=2.0):
    """Helper function to apply exponential backoff to API calls."""
    for attempt in range(max_attempts):
        try:
            return await fn()
        except retryable_exceptions as e:
            # Do not retry on Bad Request (HTTP 400) which implies our input is malformed
            if hasattr(e, "code") and getattr(e, "code") == 400:
                raise
            if attempt == max_attempts - 1:
                raise
            delay = base ** attempt + random.uniform(0, 1)
            await asyncio.sleep(delay)


class Model(Protocol):
    model_name: str
    provider: str

    async def complete(self, messages: list[dict], max_tokens: int) -> str: ...


class ClaudeModel:
    """Default model_name: 'claude-sonnet-4-6'. Uses the anthropic SDK."""

    provider = "anthropic"

    def __init__(self, model_name: str = "claude-sonnet-4-7") -> None:
        self.model_name = model_name
        self.client = anthropic.AsyncAnthropic()

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        # Extract system prompt if present
        system = next((m["content"] for m in messages if m["role"] == "system"), anthropic.NOT_GIVEN)
        convo = [m for m in messages if m["role"] != "system"]

        async def _call():
            response = await self.client.messages.create(
                model=self.model_name,
                system=system,
                messages=convo,
                max_tokens=max_tokens,
            )
            return response.content[0].text

        return await _with_backoff(
            _call,
            (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError)
        )


class OpenAIModel:
    """Uses the openai SDK."""

    provider = "openai"

    def __init__(self, model_name: str = "gpt-5") -> None:
        self.model_name = model_name
        self.client = openai.AsyncOpenAI()

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        async def _call():
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_completion_tokens=max_tokens,
            )
            return response.choices[0].message.content

        return await _with_backoff(
            _call,
            (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)
        )


class GeminiModel:
    """Uses google-genai."""

    provider = "google"

    def __init__(self, model_name: str = "gemini-2.5-pro") -> None:
        self.model_name = model_name
        self.client = google.genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        # Extract system prompt and align role names
        system = next((m["content"] for m in messages if m["role"] == "system"), None)
        convo = []
        for m in messages:
            if m["role"] == "system":
                continue
            role = "model" if m["role"] == "assistant" else m["role"]
            convo.append({"role": role, "parts": [{"text": m["content"]}]})

        config = google.genai.types.GenerateContentConfig(max_output_tokens=max_tokens)
        if system:
            config.system_instruction = system

        async def _call():
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=convo,
                config=config,
            )
            return response.text

        return await _with_backoff(
            _call,
            (google.genai.errors.APIError,)
        )


class WaferModel:
    """Uses Wafer AI for GLM and Qwen models."""
    
    provider = "wafer"

    def __init__(self, model_name: str = "glm-4") -> None:
        self.model_name = model_name
        self.client = openai.AsyncOpenAI(
            api_key=os.environ.get("WAFER_API_KEY"),
            base_url=os.environ.get("WAFER_BASE_URL", "https://api.wafer.ai/v1")
        )

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        async def _call():
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,  # Use standard max_tokens for older compatible APIs
            )
            return response.choices[0].message.content

        return await _with_backoff(
            _call,
            (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)
        )
