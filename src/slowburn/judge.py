"""LLM-as-judge using claude-opus-4-6.

Owner: Shreyas. See ROLES.md.

Takes a Probe and a response, applies the probe's rubric, returns a Verdict.
Use structured output (JSON schema) so verdicts are reliably parseable.
"""

from slowburn.probes.base import Probe, Verdict


async def judge(probe: Probe, response: str) -> Verdict:
    raise NotImplementedError("TODO(shreyas): implement structured-output judge against claude-opus-4-6")
