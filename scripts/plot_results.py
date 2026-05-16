"""Generate degradation curves and summary table from results JSONL.

Owner: Shreyas. See ROLES.md.

Usage:
    uv run python scripts/plot_results.py
"""

from pathlib import Path

from slowburn.analysis import aggregate


def main() -> None:
    aggregate(Path("results/matrix.jsonl"))


if __name__ == "__main__":
    main()
