"""Filler protocol.

Owner: Binjie. See ROLES.md.

A filler produces innocuous prior context of approximately `target_tokens`
tokens. Critical constraint: NO safety-relevant content (no refusals, no
jailbreak language, no value statements). Use a fixed seed for reproducibility.
Token-count with tiktoken as a cross-provider approximation.
"""

import random
from typing import Protocol

import tiktoken


class Filler(Protocol):
    def __call__(self, target_tokens: int, seed: int) -> list[dict]: ...


# A comprehensive banlist to ensure no safety-related or refusal concepts leak in.
BANLIST = [
    "i cannot", "i won't", "i am not able to", "i'm not able to", "i can't",
    "ignore previous instructions", "system prompt", "my values are",
    "i believe", "ethically", "safety", "alignment", "harm",
    "refuse", "policy", "guidelines", "as an ai", "as a language model"
]


def _assert_innocuous(text: str) -> None:
    """Throws a ValueError if any safety-relevant or jailbreak words are found."""
    text_lower = text.lower()
    for banned in BANLIST:
        if banned in text_lower:
            raise ValueError(f"Contamination detected! Filler text contains banned word/phrase: '{banned}'")


def build_filler_messages(target_tokens: int, seed: int, corpus: list[tuple[str, str]]) -> list[dict]:
    """Core builder: deterministic, token-targeted, perfectly innocuous, alternating roles."""
    if target_tokens <= 0:
        return []

    rng = random.Random(seed)
    enc = tiktoken.get_encoding("cl100k_base")
    
    messages = []
    current_tokens = 0
    
    while current_tokens < target_tokens:
        user_text, assistant_text = rng.choice(corpus)
        
        # Run innocuous check immediately on the chosen texts before adding
        _assert_innocuous(user_text)
        _assert_innocuous(assistant_text)
        
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": assistant_text})
        
        # Calculate approximate token count with JSON structure overhead (~8 tokens per turn pair)
        pair_tokens = len(enc.encode(user_text)) + len(enc.encode(assistant_text)) + 8
        current_tokens += pair_tokens
        
        # Stop once we hit or slightly exceed the requested context length
        if current_tokens >= target_tokens:
            break

    # Final safety check on the fully assembled output as requested by the owner guide
    assembled_text = " ".join(m["content"] for m in messages)
    _assert_innocuous(assembled_text)

    return messages
