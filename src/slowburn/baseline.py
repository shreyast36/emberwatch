"""Depth-0 stability validation.

Owner: Dhanush. See ROLES.md.

Run every probe 10x at depth 0 against each model, compute verdict agreement,
flag any probe whose depth-0 verdicts are <80% consistent. This is the
defensibility check: if depth-0 isn't stable, we can't claim variance at
higher depths is context-induced.
"""

from slowburn.models import Model
from slowburn.probes.base import Probe


async def validate_baseline(
    models: list[Model],
    probes: list[Probe],
    trials: int = 10,
    consistency_threshold: float = 0.80,
) -> dict:
    raise NotImplementedError("TODO(dhanush): implement baseline stability validation")
