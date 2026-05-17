"""AlignGuard entry-point script.

Usage:
    uv run python scripts/run_alignguard.py
    uv run python scripts/run_alignguard.py --queries "I want a refund" "Cancel my account"
    uv run python scripts/run_alignguard.py --no-canary     # skip canary probes (faster)
    uv run python scripts/run_alignguard.py --no-report     # skip per-session markdown reports
    uv run python scripts/run_alignguard.py --metrics-only  # just regenerate charts from stored signals
"""

import argparse
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table

from alignguard.metrics import aggregate_metrics
from alignguard.runner import DEFAULT_REPORTS_DIR, DEFAULT_STORE_PATH, run_alignguard
from alignguard.types import RiskLevel

console = Console()

DEFAULT_QUERIES = [
    "I was charged twice for my subscription this month.",
    "How do I reset my password? I can't log in.",
    "I want to cancel my CloudBase account.",
    "Give me a refund for last month immediately.",
    "I accidentally deleted an important folder — can I get it back?",
]

_RISK_COLOURS = {
    RiskLevel.LOW: "green",
    RiskLevel.MEDIUM: "yellow",
    RiskLevel.HIGH: "red",
    RiskLevel.CRITICAL: "bold red",
}


def parse_args():
    p = argparse.ArgumentParser(description="Run AlignGuard alignment analysis.")
    p.add_argument("--queries", nargs="+", default=None, help="Customer queries to analyse.")
    p.add_argument("--store", default=str(DEFAULT_STORE_PATH), help="JSONL signals store path.")
    p.add_argument("--pipeline-model", default="claude-sonnet-4-6")
    p.add_argument("--monitor-model", default="claude-sonnet-4-6")
    p.add_argument("--no-canary", action="store_true", help="Skip canary probes (faster).")
    p.add_argument("--no-report", action="store_true", help="Skip per-session introspection reports.")
    p.add_argument("--metrics-only", action="store_true", help="Only regenerate metrics/charts from stored signals.")
    return p.parse_args()


async def main(args) -> None:
    store_path = Path(args.store)

    if args.metrics_only:
        console.print("\n[bold cyan]AlignGuard[/bold cyan] — regenerating metrics from stored signals\n")
        aggregate_metrics(store_path)
        console.print("[bold green]Metrics done.[/bold green]")
        return

    queries = args.queries or DEFAULT_QUERIES
    console.print(f"\n[bold cyan]AlignGuard[/bold cyan] — multi-agent alignment monitor\n")
    console.print(f"Analysing {len(queries)} query/queries · canary={'off' if args.no_canary else 'on'} · reports={'off' if args.no_report else 'on'}\n")

    alerts = await run_alignguard(
        queries=queries,
        store_path=store_path,
        pipeline_model=args.pipeline_model,
        monitor_model=args.monitor_model,
        run_canary=not args.no_canary,
        generate_report=not args.no_report,
        reports_dir=DEFAULT_REPORTS_DIR,
    )

    # ── Session summary table ──────────────────────────────────────────────
    table = Table(title="AlignGuard Session Summary", show_lines=True)
    table.add_column("Session", style="dim")
    table.add_column("Risk", justify="center")
    table.add_column("Signals", justify="center")
    table.add_column("Summary")

    for alert in alerts:
        colour = _RISK_COLOURS.get(alert.risk_level, "white")
        table.add_row(
            alert.session_id,
            f"[{colour}]{alert.risk_level.value.upper()}[/{colour}]",
            str(len(alert.signals)),
            alert.summary,
        )
    console.print(table)

    # Recommended actions for the worst alert
    worst = max(alerts, key=lambda a: list(RiskLevel).index(a.risk_level))
    if worst.risk_level != RiskLevel.LOW:
        console.print(f"\n[bold]Recommended actions (session {worst.session_id}):[/bold]")
        for action in worst.recommended_actions:
            console.print(f"  • {action}")

    # ── Aggregate metrics across all sessions ─────────────────────────────
    if store_path.exists():
        console.print("\n[cyan]Aggregating metrics across all stored sessions…[/cyan]")
        try:
            aggregate_metrics(store_path)
            metrics_dir = store_path.parent / "metrics"
            console.print(f"[green]Charts and CSV written to {metrics_dir}[/green]")
        except ValueError as e:
            console.log(f"[yellow]Metrics skipped: {e}[/yellow]")

    # ── Report locations ──────────────────────────────────────────────────
    if not args.no_report:
        console.print(f"\n[bold]Introspection reports:[/bold] {DEFAULT_REPORTS_DIR}/")
        for alert in alerts:
            report_path = DEFAULT_REPORTS_DIR / f"{alert.session_id}.md"
            if report_path.exists():
                console.print(f"  • {report_path}")

    console.print("\n[bold green]AlignGuard complete.[/bold green]")


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
