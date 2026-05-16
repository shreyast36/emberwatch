"""Registry of all probes.

Owner: Dhanush. See ROLES.md.

Each probe module exposes a top-level `PROBE: Probe` instance. The registry
is the single source of truth used by the runner and baseline scripts.
"""

from slowburn.probes.base import Probe
from slowburn.probes import refusal, sycophancy, instruction_hierarchy, uncertainty, values

ALL_PROBES: list[Probe] = [
    refusal.PROBE,
    sycophancy.PROBE,
    instruction_hierarchy.PROBE,
    uncertainty.PROBE,
    values.PROBE,
]

PROBES_BY_NAME: dict[str, Probe] = {p.name: p for p in ALL_PROBES}
