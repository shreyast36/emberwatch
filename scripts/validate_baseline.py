"""Run probes at depth 0 to confirm verdict stability.

Owner: Dhanush. See ROLES.md.

Usage:
    uv run python scripts/validate_baseline.py
    uv run python scripts/validate_baseline.py --trials 3 --models claude,openai
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from slowburn.baseline import validate_baseline
from slowburn.models import ClaudeModel, GeminiModel, OpenAIModel, WaferModel
from slowburn.probes import ALL_PROBES


DEFAULT_OUTPUT_PATH = Path("results/baseline.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate depth-0 probe stability.")
    parser.add_argument("--trials", type=int, default=10, help="Trials per model/probe pair.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="Minimum mode-verdict agreement required to pass.",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="claude,openai,gemini",
        help="Comma-separated providers: claude, openai, gemini, wafer.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the JSON baseline report.",
    )
    return parser.parse_args()


def build_models(model_names: str):
    requested = {name.strip().lower() for name in model_names.split(",") if name.strip()}
    models = []

    if "claude" in requested:
        models.append(ClaudeModel("claude-sonnet-4-6"))
    if "openai" in requested:
        models.append(OpenAIModel("gpt-4o"))
    if "gemini" in requested:
        models.append(GeminiModel("gemini-2.5-pro"))
    if "wafer" in requested:
        models.append(WaferModel("glm-4"))

    unknown = requested - {"claude", "openai", "gemini", "wafer"}
    if unknown:
        raise ValueError(f"Unknown model provider(s): {', '.join(sorted(unknown))}")
    if not models:
        raise ValueError("No models selected")

    return models


def validate_required_env(model_names: str) -> None:
    requested = {name.strip().lower() for name in model_names.split(",") if name.strip()}
    required = {"ANTHROPIC_API_KEY"}

    if "openai" in requested:
        required.add("OPENAI_API_KEY")
    if "gemini" in requested:
        required.add("GOOGLE_API_KEY")
    if "wafer" in requested:
        required.add("WAFER_API_KEY")

    missing = sorted(name for name in required if not os.environ.get(name))
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")


def serialize_report(summary: dict) -> list[dict]:
    rows = []
    for (model_name, probe_name), stats in sorted(summary.items()):
        rows.append(
            {
                "model_name": model_name,
                "probe_name": probe_name,
                "passing": stats["passing"],
                "consistency": stats["consistency"],
                "mode_verdict": stats["mode_verdict"],
                "verdict_counts": stats["verdict_counts"],
                "trials": stats["trials"],
                "results": [result.model_dump() for result in stats["results"]],
            }
        )
    return rows


def print_report(summary: dict, threshold: float) -> None:
    table = Table(title=f"Depth-0 Baseline Stability (threshold {threshold:.0%})")
    table.add_column("Model", style="cyan")
    table.add_column("Probe", style="magenta")
    table.add_column("Mode")
    table.add_column("Consistency", justify="right")
    table.add_column("Counts")
    table.add_column("Status")

    for (model_name, probe_name), stats in sorted(summary.items()):
        status = "[green]PASS[/green]" if stats["passing"] else "[red]FAIL[/red]"
        counts = ", ".join(
            f"{verdict}={count}" for verdict, count in sorted(stats["verdict_counts"].items())
        )
        table.add_row(
            model_name,
            probe_name,
            stats["mode_verdict"],
            f"{stats['consistency']:.0%}",
            counts,
            status,
        )

    console = Console()
    console.print(table)


async def main() -> None:
    args = parse_args()
    load_dotenv()
    validate_required_env(args.models)

    models = build_models(args.models)
    summary = await validate_baseline(
        models=models,
        probes=ALL_PROBES,
        trials=args.trials,
        consistency_threshold=args.threshold,
    )

    print_report(summary, args.threshold)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(serialize_report(summary), indent=2), encoding="utf-8")
    Console().print(f"Wrote baseline report to [bold]{args.out}[/bold]")


if __name__ == "__main__":
    asyncio.run(main())
