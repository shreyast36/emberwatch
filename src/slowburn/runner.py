"""Async matrix runner.

Owner: Shreyas. See ROLES.md.

run_matrix(models, probes, depths, trials_per_cell, filler_strategy, output_path)
- asyncio.gather with a per-provider semaphore (default 5 in-flight)
- writes each ProbeResult to JSONL as it completes
- idempotent: resumes from existing output, keyed on (model, probe, depth, trial)
- 3x retry per cell before recording verdict="error"
"""

import asyncio
import json
from pathlib import Path

from rich.console import Console

from slowburn.fillers.base import Filler
from slowburn.judge import judge
from slowburn.models import Model
from slowburn.probes.base import Probe, ProbeResult

console = Console()

DEFAULT_PROVIDER_CONCURRENCY = 5
MAX_CELL_ATTEMPTS = 3
# 4096 leaves room for reasoning models (gpt-5 spends output budget on internal
# reasoning tokens before emitting content). At 1024, gpt-5 routinely produced
# empty content, which falsely scored as 'pass' via the empty-output rubric path
# and hid any depth-induced degradation. 4096 gives ~2-3k reasoning + ~1-2k content.
MAX_RESPONSE_TOKENS = 4096
VALUES_PROBE_NAME = "values"

# (provider, probe.name) pairs we skip entirely. Empty now that the refusal probe was
# moved off CBRN content — kept as a hook for future per-provider exclusions.
SKIP_PAIRS: set[tuple[str, str]] = set()

CellKey = tuple[str, str, int, int]


def _scan_existing(
    output_path: Path,
) -> tuple[set[CellKey], dict[str, str]]:
    """Read existing JSONL once: return (done-cell set, values depth-0 responses by model)."""
    done: set[CellKey] = set()
    values_baselines: dict[str, str] = {}
    if not output_path.exists():
        return done, values_baselines
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                console.log(f"[yellow]skipping malformed JSONL line[/yellow]")
                continue
            try:
                key: CellKey = (
                    row["model_name"],
                    row["probe_name"],
                    int(row["depth"]),
                    int(row["trial"]),
                )
            except (KeyError, TypeError, ValueError):
                continue
            done.add(key)
            if (
                row.get("probe_name") == VALUES_PROBE_NAME
                and int(row.get("depth", -1)) == 0
                and row.get("verdict") != "error"
            ):
                values_baselines[row["model_name"]] = row.get("response", "")
    return done, values_baselines


async def _writer_task(output_path: Path, queue: "asyncio.Queue[ProbeResult | None]") -> None:
    """Single writer; one row per cell, flushed immediately. Append-only."""
    with output_path.open("a", encoding="utf-8") as f:
        while True:
            item = await queue.get()
            try:
                if item is None:
                    return
                f.write(item.model_dump_json() + "\n")
                f.flush()
            finally:
                queue.task_done()


def _format_response_for_judge(probe: Probe, response_text: str, baseline_response: str | None) -> str:
    """Values probe needs the depth-0 baseline alongside the current response."""
    if probe.name != VALUES_PROBE_NAME or baseline_response is None:
        return response_text
    return (
        "<depth_0_baseline_for_same_model>\n"
        f"{baseline_response}\n"
        "</depth_0_baseline_for_same_model>\n\n"
        "<current_response>\n"
        f"{response_text}\n"
        "</current_response>"
    )


async def _run_cell(
    model: Model,
    probe: Probe,
    depth: int,
    trial: int,
    filler_strategy: Filler,
    semaphore: asyncio.Semaphore,
    queue: "asyncio.Queue[ProbeResult | None]",
    values_baselines: dict[str, str],
    values_baseline_events: dict[str, asyncio.Event],
) -> None:
    # Build the message list: filler context + the probe's own turns.
    filler_messages = filler_strategy(target_tokens=depth, seed=trial) if depth > 0 else []
    messages = filler_messages + list(probe.messages)

    # Values probe at depth > 0 needs to wait for this model's depth-0 baseline.
    baseline_response: str | None = None
    if probe.name == VALUES_PROBE_NAME and depth > 0:
        event = values_baseline_events.setdefault(model.model_name, asyncio.Event())
        await event.wait()
        baseline_response = values_baselines.get(model.model_name)

    response_text = ""
    verdict_label = "error"
    reasoning = ""
    last_error: Exception | None = None

    # Values probe at depth 0: this trial IS the baseline. Skip the judge and auto-pass —
    # the rubric is a drift-vs-baseline check, and drift against self is trivially zero.
    is_values_baseline = probe.name == VALUES_PROBE_NAME and depth == 0
    max_attempts = 1 if is_values_baseline else MAX_CELL_ATTEMPTS

    for attempt in range(max_attempts):
        try:
            async with semaphore:
                response_text = await model.complete(messages, max_tokens=MAX_RESPONSE_TOKENS)
            if is_values_baseline:
                verdict_label = "pass"
                reasoning = "depth-0 values trial — establishes the baseline; no drift to score."
                last_error = None
                break
            judge_input = _format_response_for_judge(probe, response_text, baseline_response)
            verdict = await judge(probe, judge_input)
            verdict_label = verdict.verdict
            reasoning = verdict.reasoning
            last_error = None
            break
        except Exception as e:  # noqa: BLE001 — runner records errors instead of dropping cells
            last_error = e
            console.log(
                f"[yellow]cell attempt {attempt + 1}/{MAX_CELL_ATTEMPTS} failed[/yellow] "
                f"({model.model_name}/{probe.name}/d={depth}/t={trial}): {e!r}"
            )
            await asyncio.sleep(2 ** attempt)

    if last_error is not None:
        verdict_label = "error"
        reasoning = repr(last_error)
        console.log(
            f"[red]cell failed after {MAX_CELL_ATTEMPTS} attempts[/red] "
            f"({model.model_name}/{probe.name}/d={depth}/t={trial})"
        )

    # Publish the depth-0 values baseline so depth>0 waiters can proceed.
    if probe.name == VALUES_PROBE_NAME and depth == 0 and last_error is None:
        values_baselines[model.model_name] = response_text
        values_baseline_events.setdefault(model.model_name, asyncio.Event()).set()

    result = ProbeResult(
        probe_name=probe.name,
        model_name=model.model_name,
        depth=depth,
        trial=trial,
        response=response_text,
        verdict=verdict_label,
        reasoning=reasoning,
    )
    await queue.put(result)


async def run_matrix(
    models: list[Model],
    probes: list[Probe],
    depths: list[int],
    trials_per_cell: int,
    filler_strategy: Filler,
    output_path: Path,
    per_provider_concurrency: int = DEFAULT_PROVIDER_CONCURRENCY,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    done, hydrated_values_baselines = _scan_existing(output_path)
    console.log(f"[cyan]resuming with {len(done)} cells already complete[/cyan]")

    # One semaphore per provider actually present in the model set.
    providers = {m.provider for m in models}
    semaphores: dict[str, asyncio.Semaphore] = {
        p: asyncio.Semaphore(per_provider_concurrency) for p in providers
    }

    # Values-probe baseline coordination: shared dict + per-model Event.
    values_baselines: dict[str, str] = dict(hydrated_values_baselines)
    values_baseline_events: dict[str, asyncio.Event] = {}
    if any(p.name == VALUES_PROBE_NAME for p in probes):
        for m in models:
            event = asyncio.Event()
            if m.model_name in values_baselines:
                event.set()
            values_baseline_events[m.model_name] = event

    queue: asyncio.Queue[ProbeResult | None] = asyncio.Queue()
    writer = asyncio.create_task(_writer_task(output_path, queue))

    tasks: list[asyncio.Task] = []
    skipped = 0
    for model in models:
        for probe in probes:
            if (model.provider, probe.name) in SKIP_PAIRS:
                continue
            for depth in depths:
                for trial in range(trials_per_cell):
                    key: CellKey = (model.model_name, probe.name, depth, trial)
                    if key in done:
                        skipped += 1
                        continue
                    tasks.append(asyncio.create_task(
                        _run_cell(
                            model=model,
                            probe=probe,
                            depth=depth,
                            trial=trial,
                            filler_strategy=filler_strategy,
                            semaphore=semaphores[model.provider],
                            queue=queue,
                            values_baselines=values_baselines,
                            values_baseline_events=values_baseline_events,
                        )
                    ))

    console.log(f"[cyan]scheduling {len(tasks)} cells (skipped {skipped})[/cyan]")

    try:
        if tasks:
            await asyncio.gather(*tasks)
    finally:
        await queue.put(None)
        await writer

    console.log("[green]matrix run complete[/green]")
