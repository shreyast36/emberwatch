"""Depth-0 stability validation.

Owner: Dhanush. See ROLES.md.

Run every probe 10x at depth 0 against each model, compute verdict agreement,
flag any probe whose depth-0 verdicts are <80% consistent. This is the
defensibility check: if depth-0 isn't stable, we can't claim variance at
higher depths is context-induced.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Any

from slowburn.models import Model
from slowburn.probes.base import Probe, ProbeResult
from slowburn.runner import run_matrix


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

    # 1. Call into the runner Shreyas wrote
    baseline_path = Path("results/baseline.jsonl")
    
    def empty_filler(target_tokens: int, seed: int) -> list[dict]:
        return []

    await run_matrix(
        models=models,
        probes=probes,
        depths=[0],
        trials_per_cell=trials,
        filler_strategy=empty_filler,
        output_path=baseline_path,
    )

    # 2. Read the JSONL it writes
    results = []
    if baseline_path.exists():
        with baseline_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    if int(row.get("depth", -1)) == 0:
                        results.append(ProbeResult(**row))
                except Exception:
                    continue

    return _summarize_results(results, consistency_threshold)
