"""FastAPI backend for the SlowBurn UI."""

import json
import sys
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from slowburn.analysis import aggregate
from slowburn.baseline import validate_baseline
from slowburn.fillers import generate_coding_filler, generate_qa_filler
from slowburn.models import ClaudeModel, GeminiModel, OpenAIModel, WaferModel
from slowburn.probes import ALL_PROBES, PROBES_BY_NAME
from slowburn.runner import run_matrix

app = FastAPI(title="SlowBurn API", description="AI Safety Degradation Testing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_tasks: dict[str, dict] = {}

RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MODEL_DEFAULTS: dict[str, tuple[str, type]] = {
    "claude": ("claude-sonnet-4-7", ClaudeModel),
    "openai": ("gpt-4o", OpenAIModel),
    "gemini": ("gemini-2.5-pro", GeminiModel),
    "wafer": ("glm-4", WaferModel),
}

FILLER_MAP = {
    "qa": generate_qa_filler,
    "coding": generate_coding_filler,
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _new_task(kind: str) -> tuple[str, dict]:
    tid = str(uuid.uuid4())
    task: dict = {
        "kind": kind,
        "status": "running",
        "progress": 0,
        "total": 0,
        "log": [],
        "result": None,
        "error": None,
    }
    _tasks[tid] = task
    return tid, task


def _build_models(names: list[str]) -> list:
    out = []
    for n in names:
        if n not in MODEL_DEFAULTS:
            raise ValueError(f"Unknown model '{n}'. Choose from: {list(MODEL_DEFAULTS)}")
        default_name, cls = MODEL_DEFAULTS[n]
        out.append(cls(default_name))
    return out


# ── Request schemas ────────────────────────────────────────────────────────────

class BaselineRequest(BaseModel):
    models: list[str] = ["claude"]
    probes: list[str] = []
    trials: int = 5
    threshold: float = 0.80


class MatrixRequest(BaseModel):
    models: list[str] = ["claude"]
    probes: list[str] = []
    depths: list[int] = [0, 5000, 25000]
    trials: int = 3
    filler: str = "qa"


# ── Health / meta ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/probes")
def list_probes():
    return [
        {"name": p.name, "failure_mode": p.failure_mode, "rubric": p.rubric}
        for p in ALL_PROBES
    ]


@app.get("/models")
def list_models():
    return list(MODEL_DEFAULTS)


# ── Task status ────────────────────────────────────────────────────────────────

@app.get("/task/{tid}")
def get_task(tid: str):
    if tid not in _tasks:
        raise HTTPException(404, "Task not found")
    t = _tasks[tid]
    return {
        "kind": t["kind"],
        "status": t["status"],
        "progress": t["progress"],
        "total": t["total"],
        "log": t["log"][-30:],
        "error": t["error"],
    }


@app.get("/task/{tid}/result")
def get_task_result(tid: str):
    if tid not in _tasks:
        raise HTTPException(404, "Task not found")
    return _tasks[tid].get("result")


# ── Baseline ───────────────────────────────────────────────────────────────────

@app.post("/baseline/run")
async def run_baseline_endpoint(req: BaselineRequest, bg: BackgroundTasks):
    tid, _ = _new_task("baseline")
    bg.add_task(_baseline_bg, tid, req)
    return {"task_id": tid}


async def _baseline_bg(tid: str, req: BaselineRequest) -> None:
    task = _tasks[tid]
    try:
        models = _build_models(req.models)
        probes = [PROBES_BY_NAME[p] for p in req.probes] if req.probes else ALL_PROBES
        task["total"] = len(models) * len(probes) * req.trials
        task["log"].append(
            f"Starting: {len(models)} model(s) × {len(probes)} probe(s) × {req.trials} trial(s)"
        )

        summary = await validate_baseline(
            models=models,
            probes=probes,
            trials=req.trials,
            consistency_threshold=req.threshold,
        )

        rows = []
        for (model_name, probe_name), stats in sorted(summary.items()):
            rows.append(
                {
                    "model_name": model_name,
                    "probe_name": probe_name,
                    "consistency": stats["consistency"],
                    "passing": stats["passing"],
                    "mode_verdict": stats["mode_verdict"],
                    "verdict_counts": stats["verdict_counts"],
                    "trials": stats["trials"],
                    "results": [r.model_dump() for r in stats["results"]],
                }
            )

        out = RESULTS_DIR / "baseline.json"
        out.write_text(json.dumps(rows, indent=2), encoding="utf-8")

        task["status"] = "completed"
        task["result"] = rows
        task["log"].append("Done.")
    except Exception as exc:
        task["status"] = "error"
        task["error"] = str(exc)
        task["log"].append(f"Error: {exc}")


@app.get("/baseline/results")
def get_baseline_results():
    path = RESULTS_DIR / "baseline.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ── Matrix ─────────────────────────────────────────────────────────────────────

@app.post("/matrix/run")
async def run_matrix_endpoint(req: MatrixRequest, bg: BackgroundTasks):
    tid, _ = _new_task("matrix")
    bg.add_task(_matrix_bg, tid, req)
    return {"task_id": tid}


async def _matrix_bg(tid: str, req: MatrixRequest) -> None:
    task = _tasks[tid]
    try:
        models = _build_models(req.models)
        probes = [PROBES_BY_NAME[p] for p in req.probes] if req.probes else ALL_PROBES
        filler = FILLER_MAP.get(req.filler, generate_qa_filler)
        output_path = RESULTS_DIR / "matrix.jsonl"

        total = len(models) * len(probes) * len(req.depths) * req.trials
        task["total"] = total
        task["log"].append(
            f"Starting: {len(models)}m × {len(probes)}p × {len(req.depths)}d × {req.trials}t = {total} cells"
        )

        await run_matrix(
            models=models,
            probes=probes,
            depths=req.depths,
            trials_per_cell=req.trials,
            filler_strategy=filler,
            output_path=output_path,
        )

        count = sum(
            1 for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()
        )
        task["status"] = "completed"
        task["result"] = {"rows_written": count}
        task["log"].append(f"Done. {count} rows written to {output_path.name}.")
    except Exception as exc:
        task["status"] = "error"
        task["error"] = str(exc)
        task["log"].append(f"Error: {exc}")


@app.get("/matrix/count")
def get_matrix_count():
    path = RESULTS_DIR / "matrix.jsonl"
    if not path.exists():
        return {"count": 0}
    count = sum(
        1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )
    return {"count": count}


@app.get("/matrix/results")
def get_matrix_results(limit: int = 200):
    path = RESULTS_DIR / "matrix.jsonl"
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
                if len(rows) >= limit:
                    break
    return rows


# ── Analysis ───────────────────────────────────────────────────────────────────

@app.post("/analysis/run")
def run_analysis():
    path = RESULTS_DIR / "matrix.jsonl"
    if not path.exists():
        raise HTTPException(400, "No matrix results. Run the matrix experiment first.")
    try:
        aggregate(path)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    plots = sorted(p.name for p in RESULTS_DIR.glob("*.png"))
    return {"plots": plots, "has_csv": (RESULTS_DIR / "summary.csv").exists()}


@app.get("/analysis/plots")
def list_plots():
    return sorted(p.name for p in RESULTS_DIR.glob("*.png"))


@app.get("/analysis/plot/{name}")
def get_plot(name: str):
    if not name.endswith(".png"):
        raise HTTPException(400, "PNG files only")
    path = RESULTS_DIR / name
    if not path.exists():
        raise HTTPException(404, "Plot not found")
    return FileResponse(str(path), media_type="image/png")


@app.get("/analysis/csv")
def get_csv():
    path = RESULTS_DIR / "summary.csv"
    if not path.exists():
        raise HTTPException(404, "No CSV yet. Run analysis first.")
    return path.read_text(encoding="utf-8")
