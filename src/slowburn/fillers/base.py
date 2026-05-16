"""Filler protocol.

Owner: Binjie. See ROLES.md.

A filler produces innocuous prior context of approximately `target_tokens`
tokens. Critical constraint: NO safety-relevant content (no refusals, no
jailbreak language, no value statements). Use a fixed seed for reproducibility.
Token-count with tiktoken as a cross-provider approximation.
"""

from typing import Protocol


class Filler(Protocol):
    def __call__(self, target_tokens: int, seed: int) -> list[dict]: ...
