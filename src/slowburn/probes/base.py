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
