"""Aggregate JSONL results into degradation curves and a summary CSV.

Owner: Shreyas. See ROLES.md.

- Read results JSONL
- Aggregate by (model, probe, depth) -> pass-rate (with sample size for error bars)
- Plot one matplotlib figure per probe (one line per model, pass-rate vs. depth)
- Plot a comparative half-life figure per model (one line per probe, normalized
  to depth-0 = 1.0) — this is the project's headline finding: the relative
  fragility ordering across safety properties under pure depth stress. See
  README and docs/RELATED_WORK.md for the positioning vs. prior work.
- Save figures as PNG into results/
- Emit a model x probe x depth pivot of pass-rates as CSV
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from rich.console import Console

console = Console()


def _load_results(results_path: Path) -> pd.DataFrame:
    if not results_path.exists():
        raise FileNotFoundError(f"results file not found: {results_path}")
    df = pd.read_json(results_path, lines=True)
    if df.empty:
        raise ValueError(f"results file is empty: {results_path}")
    required = {"model_name", "probe_name", "depth", "trial", "verdict"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"results file missing required columns: {sorted(missing)}")
    df["depth"] = df["depth"].astype(int)
    return df


def _per_cell_stats(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (model, probe, depth) with pass_rate, n, n_errors, stderr."""
    grouped = df.groupby(["model_name", "probe_name", "depth"], sort=True)
    rows = []
    for (model_name, probe_name, depth), cell in grouped:
        n = len(cell)
        n_errors = int((cell["verdict"] == "error").sum())
        n_scored = n - n_errors
        n_pass = int((cell["verdict"] == "pass").sum())
        pass_rate = (n_pass / n_scored) if n_scored > 0 else float("nan")
        # Wilson/normal approximation stderr on the scored subset; NaN if degenerate.
        if n_scored > 0 and not math.isnan(pass_rate):
            stderr = math.sqrt(pass_rate * (1 - pass_rate) / n_scored)
        else:
            stderr = float("nan")
        rows.append({
            "model_name": model_name,
            "probe_name": probe_name,
            "depth": int(depth),
            "n": n,
            "n_errors": n_errors,
            "n_scored": n_scored,
            "pass_rate": pass_rate,
            "stderr": stderr,
        })
    return pd.DataFrame(rows)


def _plot_probe(probe_name: str, probe_df: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for model_name, sub in probe_df.groupby("model_name", sort=True):
        sub = sub.sort_values("depth")
        ax.errorbar(
            sub["depth"],
            sub["pass_rate"],
            yerr=sub["stderr"],
            marker="o",
            capsize=3,
            label=model_name,
        )
    ax.set_xlabel("Prior-context depth (tokens)")
    ax.set_ylabel("Pass rate")
    ax.set_title(f"Degradation curve — {probe_name}")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_half_lives(stats: pd.DataFrame, out_dir: Path) -> list[Path]:
    """One figure per model: each probe's pass-rate vs. depth, normalized to
    depth-0 = 1.0. Surfaces the *relative fragility ordering* — the headline
    finding the matrix is designed to produce."""
    written: list[Path] = []
    for model_name, model_df in stats.groupby("model_name", sort=True):
        fig, ax = plt.subplots(figsize=(9, 5.5))
        for probe_name, sub in model_df.groupby("probe_name", sort=True):
            sub = sub.sort_values("depth")
            depth_zero = sub[sub["depth"] == 0]
            if depth_zero.empty or math.isnan(depth_zero["pass_rate"].iloc[0]):
                # No depth-0 anchor — skip; plot would be misleading.
                continue
            anchor = depth_zero["pass_rate"].iloc[0]
            if anchor <= 0:
                # Cannot normalize against a zero baseline; skip.
                continue
            normalized = sub["pass_rate"] / anchor
            ax.plot(
                sub["depth"],
                normalized,
                marker="o",
                label=probe_name,
            )
        ax.set_xlabel("Prior-context depth (tokens)")
        ax.set_ylabel("Pass rate / depth-0 pass rate")
        ax.set_title(f"Safety half-lives — {model_name}")
        ax.axhline(1.0, color="grey", linestyle=":", alpha=0.5, linewidth=1)
        ax.set_ylim(-0.05, 1.15)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="best", title="probe")
        fig.tight_layout()
        out_path = out_dir / f"half_lives_{model_name}.png"
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        written.append(out_path)
    return written


def _write_summary_csv(stats: pd.DataFrame, out_path: Path) -> None:
    pivot = stats.pivot_table(
        index=["model_name", "probe_name"],
        columns="depth",
        values="pass_rate",
        aggfunc="first",
    ).sort_index()
    pivot.columns = [f"depth_{int(c)}" for c in pivot.columns]
    pivot.to_csv(out_path)


def aggregate(results_path: Path) -> None:
    results_path = Path(results_path)
    out_dir = results_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _load_results(results_path)
    console.log(f"[cyan]loaded {len(df)} rows from {results_path}[/cyan]")

    stats = _per_cell_stats(df)

    for probe_name, probe_df in stats.groupby("probe_name", sort=True):
        png_path = out_dir / f"{probe_name}.png"
        _plot_probe(probe_name, probe_df, png_path)
        console.log(f"[green]wrote {png_path}[/green]")

    for half_life_path in _plot_half_lives(stats, out_dir):
        console.log(f"[green]wrote {half_life_path}[/green]")

    summary_path = out_dir / "summary.csv"
    _write_summary_csv(stats, summary_path)
    console.log(f"[green]wrote {summary_path}[/green]")
