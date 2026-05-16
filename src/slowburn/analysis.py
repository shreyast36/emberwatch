"""Aggregate JSONL results into degradation curves and a summary CSV.

Owner: Shreyas. See ROLES.md.

- Read results JSONL
- Aggregate by (model, probe, depth) -> pass-rate
- Plot one matplotlib figure per probe (one line per model, pass-rate vs. depth)
- Save figures as PNG into results/
- Emit a model x probe x depth heatmap of pass-rates as CSV
"""

from pathlib import Path


def aggregate(results_path: Path) -> None:
    raise NotImplementedError("TODO(shreyas): aggregate + plot + write summary CSV")
