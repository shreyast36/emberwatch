"""Shared types for probes and their results.

Owner: Dhanush. See ROLES.md.
"""

from typing import Literal

from pydantic import BaseModel


class Probe(BaseModel):
    name: str
    failure_mode: str
    messages: list[dict]
    rubric: str
    # Few-shot examples for the judge. Optional but strongly recommended when the
    # judge is a smaller model (e.g. gpt-3.5-turbo) — anchors the pass/partial/fail
    # boundary on concrete cases rather than asking the judge to derive it from
    # abstract rubric text alone. Each example is {"response", "verdict", "reasoning"}.
    examples: list[dict] = []


class Verdict(BaseModel):
    verdict: Literal["pass", "fail", "partial", "error"]
    confidence: float
    reasoning: str


class ProbeResult(BaseModel):
    probe_name: str
    model_name: str
    depth: int
    trial: int
    response: str
    verdict: Literal["pass", "fail", "partial", "error"]
    reasoning: str
