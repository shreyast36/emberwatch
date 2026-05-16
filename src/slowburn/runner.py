"""Async matrix runner.

Owner: Shreyas. See ROLES.md.

run_matrix(models, probes, depths, trials_per_cell, filler_strategy, output_path)
- asyncio.gather with a per-provider semaphore (default 5 in-flight)
- writes each ProbeResult to JSONL as it completes
- idempotent: resumes from existing output, keyed on (model, probe, depth, trial)
- 3x retry per cell before recording verdict="error"
"""

from pathlib import Path

from slowburn.fillers.base import Filler
from slowburn.models import Model
from slowburn.probes.base import Probe


async def run_matrix(
    models: list[Model],
    probes: list[Probe],
    depths: list[int],
    trials_per_cell: int,
    filler_strategy: Filler,
    output_path: Path,
) -> None:
    raise NotImplementedError("TODO(shreyas): implement matrix runner")
