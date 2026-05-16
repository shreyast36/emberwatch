"""Depth-0 stability validation.

Owner: Dhanush. See ROLES.md.

Run every probe 10x at depth 0 against each model, compute verdict agreement,
flag any probe whose depth-0 verdicts are <80% consistent. This is the
defensibility check: if depth-0 isn't stable, we can't claim variance at
higher depths is context-induced.
"""

import asyncio
from collections import Counter
from typing import Any

from slowburn.judge import judge
from slowburn.models import Model
from slowburn.probes.base import Probe, ProbeResult


MAX_RESPONSE_TOKENS = 1024


def _model_name(model: Model) -> str:
    return getattr(model, "model_name", model.__class__.__name__)


async def _run_trial(model: Model, probe: Probe, trial: int) -> ProbeResult:
    model_name = _model_name(model)

    try:
        messages = [dict(message) for message in probe.messages]
        response = await model.complete(messages, max_tokens=MAX_RESPONSE_TOKENS)
        verdict = await judge(probe, response)
        return ProbeResult(
            probe_name=probe.name,
            model_name=model_name,
            depth=0,
            trial=trial,
            response=response,
            verdict=verdict.verdict,
            reasoning=verdict.reasoning,
        )
    except Exception as exc:
        return ProbeResult(
            probe_name=probe.name,
            model_name=model_name,
            depth=0,
            trial=trial,
            response="",
            verdict="error",
            reasoning=f"{exc.__class__.__name__}: {exc}",
        )


def _summarize_results(
    results: list[ProbeResult],
    consistency_threshold: float,
) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[ProbeResult]] = {}
    for result in results:
        grouped.setdefault((result.model_name, result.probe_name), []).append(result)

    summary: dict[tuple[str, str], dict[str, Any]] = {}
    for key, group in grouped.items():
        verdict_counts = Counter(result.verdict for result in group)
        mode_verdict, mode_count = verdict_counts.most_common(1)[0]
        consistency = mode_count / len(group)

        summary[key] = {
            "consistency": consistency,
            "passing": consistency >= consistency_threshold and mode_verdict != "error",
            "mode_verdict": mode_verdict,
            "verdict_counts": dict(verdict_counts),
            "trials": len(group),
            "results": group,
        }

    return summary


async def validate_baseline(
    models: list[Model],
    probes: list[Probe],
    trials: int = 10,
    consistency_threshold: float = 0.80,
) -> dict:
    """Run depth-0 trials and report verdict stability per model/probe pair.

    A pair passes when the most common verdict appears in at least
    `consistency_threshold` of trials. Error verdicts are included in the
    distribution, but an error-dominant pair never passes.
    """

    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 < consistency_threshold <= 1:
        raise ValueError("consistency_threshold must be in the range (0, 1]")

    tasks = [
        _run_trial(model, probe, trial)
        for model in models
        for probe in probes
        for trial in range(trials)
    ]
    results = await asyncio.gather(*tasks)

    return _summarize_results(results, consistency_threshold)

