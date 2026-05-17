"""AlignGuard runner — orchestrates one analysis session.

Flow:
  1. Run a customer query through the sample_system pipeline → SessionTrace
  2. Pass the trace to GamingDetector and ReasoningAuditor in parallel
  3. Run CanaryProber against the live pipeline
  4. Check DriftTracker against stored history
  5. Aggregate all signals → Alert
  6. Persist signals and alert to store
"""

import asyncio
from pathlib import Path

from rich.console import Console

from alignguard.aggregator import aggregate
from alignguard.monitors.canary_prober import CanaryProber
from alignguard.monitors.drift_tracker import DriftTracker
from alignguard.monitors.gaming_detector import GamingDetector
from alignguard.monitors.reasoning_auditor import ReasoningAuditor
from alignguard.report import generate_session_report
from alignguard.sample_system.pipeline import run_session
from alignguard.store import AlignmentStore
from alignguard.types import Alert, AlignmentSignal, SessionTrace

console = Console()

DEFAULT_STORE_PATH = Path("results/alignguard/signals.jsonl")
DEFAULT_ALERTS_PATH = Path("results/alignguard/alerts.jsonl")
DEFAULT_REPORTS_DIR = Path("results/alignguard/reports")
DEFAULT_MONITOR_MODEL = "claude-sonnet-4-6"


async def analyze_session(
    query: str,
    store: AlignmentStore,
    pipeline_model: str = "claude-sonnet-4-6",
    monitor_model: str = DEFAULT_MONITOR_MODEL,
    run_canary: bool = True,
    generate_report: bool = True,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
) -> tuple[SessionTrace, Alert]:
    """Run one query end-to-end and return the session trace + alert."""

    console.log(f"[cyan]Running pipeline for:[/cyan] {query[:80]}")
    session = await run_session(query, model=pipeline_model)
    console.log(f"[green]Session {session.session_id} complete.[/green]")

    # Agents A and B run in parallel on the same trace
    gaming = GamingDetector(model=monitor_model)
    auditor = ReasoningAuditor(model=monitor_model)
    gaming_signal, reasoning_signal = await asyncio.gather(
        gaming.analyze(session),
        auditor.analyze(session),
    )
    console.log(
        f"  Gaming score: {gaming_signal.score:.2f}  |  "
        f"Reasoning score: {reasoning_signal.score:.2f}"
    )

    signals: list[AlignmentSignal] = [gaming_signal, reasoning_signal]

    # Agent C: canary prober (optional — adds latency)
    if run_canary:
        console.log("[cyan]Running canary probes…[/cyan]")
        prober = CanaryProber(model=monitor_model)
        canary_signal = await prober.run_probes(
            run_pipeline=lambda q: run_session(q, model=pipeline_model),
            session_id=session.session_id,
        )
        console.log(f"  Canary score: {canary_signal.score:.2f}  ({canary_signal.evidence})")
        signals.append(canary_signal)

    # Agent D: drift tracker (reads history, no LLM call)
    tracker = DriftTracker(store)
    drift_signal = tracker.analyze(session.session_id)
    if drift_signal:
        console.log(f"  [yellow]Drift detected:[/yellow] {drift_signal.evidence}")
        signals.append(drift_signal)

    # Persist signals before aggregating
    for sig in signals:
        store.append_signal(sig)

    alert = aggregate(signals, session.session_id)

    if generate_report:
        console.log(f"[cyan]Generating introspection report for session {session.session_id}…[/cyan]")
        report_path = await generate_session_report(
            session=session,
            alert=alert,
            output_dir=reports_dir,
            model=monitor_model,
        )
        console.log(f"[green]Report written → {report_path}[/green]")

    return session, alert


async def run_alignguard(
    queries: list[str],
    store_path: Path = DEFAULT_STORE_PATH,
    pipeline_model: str = "claude-sonnet-4-6",
    monitor_model: str = DEFAULT_MONITOR_MODEL,
    run_canary: bool = True,
    generate_report: bool = True,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    alerts_path: Path | None = None,
    progress_cb=None,
) -> list[Alert]:
    """Run AlignGuard across a list of queries. Returns one Alert per query."""
    store = AlignmentStore(store_path)
    _alerts_path = alerts_path or DEFAULT_ALERTS_PATH
    alerts: list[Alert] = []
    for i, query in enumerate(queries):
        if progress_cb:
            progress_cb(f"[{i+1}/{len(queries)}] Running session: {query[:60]}")
        _, alert = await analyze_session(
            query=query,
            store=store,
            pipeline_model=pipeline_model,
            monitor_model=monitor_model,
            run_canary=run_canary,
            generate_report=generate_report,
            reports_dir=reports_dir,
        )
        # Override the alert path with caller-supplied path
        store.append_alert(alert, _alerts_path)
        alerts.append(alert)
        if progress_cb:
            progress_cb(f"Session {alert.session_id} done — {alert.risk_level.value.upper()}: {alert.summary[:60]}")
        console.log(
            f"[bold]Alert:[/bold] {alert.risk_level.value.upper()} — {alert.summary}"
        )
    return alerts
