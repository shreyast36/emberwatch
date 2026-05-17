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

# Safety identifier sent on every model call. OpenAI-compatible providers (openai, xai, wafer)
# accept it as the `user` field; Anthropic accepts it as metadata.user_id. Tags this traffic as
# legitimate AI-safety research so provider abuse-detection routes flags to the right team.
SAFETY_IDENTIFIER = "slowburn-ai-safety-training-research"


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
    """Default model_name: 'claude-opus-4-7'. Uses the anthropic SDK."""

    provider = "anthropic"

    def __init__(self, model_name: str = "claude-opus-4-7") -> None:
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
                metadata={"user_id": SAFETY_IDENTIFIER},
            )
            # stop_reason='refusal' yields empty content; surface that to the judge as a refusal signal.
            if response.stop_reason == "refusal" or not response.content:
                return "[model declined to produce any output (stop_reason='refusal')]"
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
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    user=SAFETY_IDENTIFIER,
                )
            except openai.BadRequestError as e:
                # OpenAI's gateway pre-screens prompts and 400s with code='invalid_prompt'
                # on bio/CBRN-adjacent content. The model never saw the request — that is
                # itself a strong refusal; surface it to the judge as such.
                # The SDK unwraps the `error` envelope, exposing code/type directly.
                if getattr(e, "code", None) == "invalid_prompt":
                    return "[model declined to produce any output (openai gateway: invalid_prompt)]"
                raise
            return response.choices[0].message.content or ""

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
            if response.text:
                return response.text
            # Empty .text usually means a safety filter or block; surface why so the judge can score it.
            block_reason = getattr(getattr(response, "prompt_feedback", None), "block_reason", None)
            finish_reason = None
            try:
                finish_reason = response.candidates[0].finish_reason
            except (AttributeError, IndexError):
                pass
            return (
                f"[model declined to produce any output "
                f"(finish_reason={finish_reason!r}, block_reason={block_reason!r})]"
            )

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
                user=SAFETY_IDENTIFIER,
            )
            return response.choices[0].message.content or ""

        return await _with_backoff(
            _call,
            (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)
        )


class GrokModel:
    """Uses xAI API (OpenAI compatible)."""
    
    provider = "xai"

    def __init__(self, model_name: str = "grok-beta") -> None:
        self.model_name = model_name
        self.client = openai.AsyncOpenAI(
            api_key=os.environ.get("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    async def complete(self, messages: list[dict], max_tokens: int) -> str:
        async def _call():
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                user=SAFETY_IDENTIFIER,
            )
            return response.choices[0].message.content or ""

        return await _with_backoff(
            _call,
            (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)
        )
