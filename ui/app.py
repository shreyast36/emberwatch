"""Streamlit frontend for SlowBurn — AI Safety Degradation Testing."""

import io
import os
import time

import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("SLOWBURN_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="SlowBurn — Safety Degradation Testing",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🔥 SlowBurn")
    st.caption("AI Safety Degradation Testing")
    st.divider()

    api_url = st.text_input("API URL", value=API_URL, key="api_url")

    _api_ok = False
    try:
        r = requests.get(f"{api_url}/health", timeout=2)
        if r.status_code == 200:
            st.success("API connected ✓")
            _api_ok = True
        else:
            st.error(f"API returned {r.status_code}")
    except Exception:
        st.error("API offline. Start it with:\n`uvicorn api.main:app --reload`")

    AVAILABLE_MODELS: list[str] = []
    AVAILABLE_PROBES: list[dict] = []
    if _api_ok:
        try:
            AVAILABLE_MODELS = requests.get(f"{api_url}/models", timeout=3).json()
            AVAILABLE_PROBES = requests.get(f"{api_url}/probes", timeout=3).json()
        except Exception:
            AVAILABLE_MODELS = ["claude", "openai"]

    st.divider()
    st.markdown(
        "**Model defaults**\n"
        "- `claude` -> claude-opus-4-7\n"
        "- `openai` -> gpt-5\n"
        "\n_Judge: grok-4.3 (reserved off-panel)_"
    )
    st.divider()
    st.caption("Experiment design: hold probe constant, vary prior-context depth. "
               "Measures whether safety properties degrade as context accumulates.")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _post(path: str, payload: dict | None = None):
    return requests.post(f"{api_url}{path}", json=payload or {}, timeout=15)


def _get(path: str, **params):
    return requests.get(f"{api_url}{path}", params=params or None, timeout=10)


def _verdict_badge(v: str) -> str:
    return {"pass": "✅ pass", "fail": "❌ fail", "partial": "⚠️ partial", "error": "💥 error"}.get(v, v)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab_baseline, tab_matrix, tab_analysis, tab_reference = st.tabs(
    ["🧪 Baseline", "🏃 Matrix Runner", "📊 Analysis", "📖 Probe Reference"]
)


# ════════════════════════════════════════════════════════════════════════════════
# Tab 1 — Baseline Validation
# ════════════════════════════════════════════════════════════════════════════════

with tab_baseline:
    st.header("Baseline Validation")
    st.write(
        "Run each probe **10× at depth 0** to confirm verdicts are stable before spending "
        "budget on the full matrix. A pair passes when its most-common verdict appears in "
        "≥ threshold of trials."
    )

    col1, col2 = st.columns(2)
    with col1:
        b_models = st.multiselect(
            "Models", AVAILABLE_MODELS, default=AVAILABLE_MODELS[:1], key="b_models"
        )
        probe_names = [p["name"] for p in AVAILABLE_PROBES]
        b_probes = st.multiselect(
            "Probes", probe_names, default=[], key="b_probes",
            help="Leave empty to test all probes."
        )

    with col2:
        b_trials = st.number_input(
            "Trials per pair", min_value=1, max_value=20, value=5, key="b_trials"
        )
        b_threshold = st.slider(
            "Consistency threshold", 0.5, 1.0, 0.80, 0.05, key="b_thresh"
        )
        n_probes_sel = len(b_probes) if b_probes else len(AVAILABLE_PROBES)
        st.metric("Total API calls", len(b_models) * n_probes_sel * b_trials)

    if st.button("▶ Run Baseline", type="primary", disabled=not _api_ok or not b_models):
        resp = _post(
            "/baseline/run",
            {
                "models": b_models,
                "probes": b_probes,
                "trials": int(b_trials),
                "threshold": b_threshold,
            },
        )
        st.session_state["b_task"] = resp.json()["task_id"]
        st.session_state.pop("b_done", None)
        st.rerun()

    # Poll status
    if "b_task" in st.session_state and "b_done" not in st.session_state:
        tid = st.session_state["b_task"]
        try:
            status = _get(f"/task/{tid}").json()
        except Exception as e:
            st.error(f"Could not reach API: {e}")
            status = {"status": "error", "error": str(e), "log": []}

        status_box = st.empty()
        prog = st.progress(0.0)

        if status["status"] == "running":
            prog.progress(0.5)
            status_box.info("⏳ Running baseline… auto-refreshing every 3 s.")
            if status["log"]:
                with st.expander("Log", expanded=False):
                    st.text("\n".join(status["log"]))
            time.sleep(3)
            st.rerun()

        elif status["status"] == "completed":
            prog.progress(1.0)
            result = _get(f"/task/{tid}/result").json()
            st.session_state["b_done"] = result
            st.rerun()

        elif status["status"] == "error":
            prog.empty()
            st.error(f"Task failed: {status['error']}")

    # Show result
    if "b_done" in st.session_state:
        rows = st.session_state["b_done"]
        all_pass = all(r["passing"] for r in rows)
        if all_pass:
            st.success(f"All {len(rows)} pair(s) passed the consistency check ✅")
        else:
            n_fail = sum(1 for r in rows if not r["passing"])
            st.warning(f"{n_fail} / {len(rows)} pair(s) failed — consider fixing those probes before running the matrix.")

        display = []
        for r in rows:
            counts = ", ".join(f"{k}={v}" for k, v in sorted(r["verdict_counts"].items()))
            display.append(
                {
                    "Model": r["model_name"],
                    "Probe": r["probe_name"],
                    "Consistency": f"{r['consistency']:.0%}",
                    "Mode verdict": _verdict_badge(r["mode_verdict"]),
                    "Counts": counts,
                    "Status": "✅ PASS" if r["passing"] else "❌ FAIL",
                }
            )
        st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)

        if st.button("Clear result", key="b_clear"):
            del st.session_state["b_task"]
            del st.session_state["b_done"]
            st.rerun()

    # Saved results
    st.divider()
    with st.expander("📂 Saved baseline results (results/baseline.json)"):
        try:
            saved = _get("/baseline/results")
            if saved.status_code == 200 and saved.json():
                rows = saved.json()
                display = []
                for r in rows:
                    counts = ", ".join(
                        f"{k}={v}" for k, v in sorted(r["verdict_counts"].items())
                    )
                    display.append(
                        {
                            "Model": r["model_name"],
                            "Probe": r["probe_name"],
                            "Consistency": f"{r['consistency']:.0%}",
                            "Mode verdict": _verdict_badge(r["mode_verdict"]),
                            "Counts": counts,
                            "Status": "✅ PASS" if r["passing"] else "❌ FAIL",
                        }
                    )
                st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
            else:
                st.info("No saved results found.")
        except Exception:
            st.info("Could not load saved results.")


# ════════════════════════════════════════════════════════════════════════════════
# Tab 2 — Matrix Runner
# ════════════════════════════════════════════════════════════════════════════════

with tab_matrix:
    st.header("Matrix Runner")
    st.write(
        "Run the full experiment grid: **model × probe × context depth × trial**. "
        "Results are written to `results/matrix.jsonl` and can be resumed if interrupted."
    )

    col1, col2 = st.columns(2)
    with col1:
        mx_models = st.multiselect(
            "Models", AVAILABLE_MODELS, default=AVAILABLE_MODELS[:1], key="mx_models"
        )
        probe_names = [p["name"] for p in AVAILABLE_PROBES]
        mx_probes = st.multiselect(
            "Probes", probe_names, default=[], key="mx_probes",
            help="Leave empty to run all probes."
        )
        mx_filler = st.selectbox(
            "Filler corpus", ["qa", "coding"], key="mx_filler",
            help="Innocuous prior-context: trivia Q&A (qa) or programming Q&A (coding)."
        )

    with col2:
        mx_trials = st.number_input("Trials per cell", 1, 20, value=3, key="mx_trials")

        DEPTH_PRESETS = {
            "Depth 0 only": [0],
            "0 + 5 k": [0, 5_000],
            "0 + 5 k + 25 k  (quick test)": [0, 5_000, 25_000],
            "0 + 5 k + 25 k + 75 k": [0, 5_000, 25_000, 75_000],
            "Full  (0, 5 k, 25 k, 75 k, 150 k)": [0, 5_000, 25_000, 75_000, 150_000],
        }
        depth_choice = st.selectbox("Context depths", list(DEPTH_PRESETS), index=2, key="mx_depth")
        mx_depths = DEPTH_PRESETS[depth_choice]
        st.caption(f"Depths: {mx_depths}")

        n_p = len(mx_probes) if mx_probes else max(len(AVAILABLE_PROBES), 1)
        total_cells = len(mx_models) * n_p * len(mx_depths) * int(mx_trials)
        st.metric("Total cells", total_cells)

    if st.button("▶ Run Matrix", type="primary", disabled=not _api_ok or not mx_models):
        resp = _post(
            "/matrix/run",
            {
                "models": mx_models,
                "probes": mx_probes,
                "depths": mx_depths,
                "trials": int(mx_trials),
                "filler": mx_filler,
            },
        )
        st.session_state["mx_task"] = resp.json()["task_id"]
        st.session_state["mx_total"] = total_cells
        st.session_state.pop("mx_done", None)
        st.rerun()

    # Poll status
    if "mx_task" in st.session_state and "mx_done" not in st.session_state:
        tid = st.session_state["mx_task"]
        try:
            status = _get(f"/task/{tid}").json()
            count_data = _get("/matrix/count").json()
        except Exception as e:
            st.error(f"Could not reach API: {e}")
            status = {"status": "error", "error": str(e), "log": [], "total": 0}
            count_data = {"count": 0}

        rows_done = count_data.get("count", 0)
        total = st.session_state.get("mx_total", max(status.get("total", 1), 1))
        frac = min(rows_done / total, 1.0)

        st.progress(frac, text=f"{rows_done} / {total} cells  ({frac:.0%})")

        if status["log"]:
            with st.expander("Log", expanded=True):
                st.code("\n".join(status["log"]), language=None)

        if status["status"] == "running":
            st.info("⏳ Running… auto-refreshing every 4 s.")
            time.sleep(4)
            st.rerun()
        elif status["status"] == "completed":
            st.session_state["mx_done"] = True
            st.rerun()
        elif status["status"] == "error":
            st.error(f"Task failed: {status['error']}")

    if "mx_done" in st.session_state:
        count_data = _get("/matrix/count").json()
        st.success(f"Matrix run complete — {count_data['count']} rows in matrix.jsonl ✅")
        if st.button("Clear", key="mx_clear"):
            del st.session_state["mx_task"]
            del st.session_state["mx_done"]
            st.rerun()

    # Results preview
    st.divider()
    st.subheader("Results preview")
    try:
        count_data = _get("/matrix/count").json()
        total_rows = count_data.get("count", 0)
    except Exception:
        total_rows = 0

    if total_rows > 0:
        data_resp = _get("/matrix/results", limit=500)
        if data_resp.status_code == 200:
            raw = data_resp.json()
            df = pd.DataFrame(raw)

            metric_cols = st.columns(4)
            metric_cols[0].metric("Total rows", total_rows)
            scored = df[df["verdict"] != "error"]
            if not scored.empty:
                pass_rate = (scored["verdict"] == "pass").mean()
                metric_cols[1].metric("Pass rate", f"{pass_rate:.0%}")
            err_rate = (df["verdict"] == "error").mean()
            metric_cols[2].metric("Error rate", f"{err_rate:.0%}")
            metric_cols[3].metric("Unique models", df["model_name"].nunique())

            # Verdict breakdown by probe
            st.subheader("Verdict breakdown by probe")
            if "probe_name" in df.columns and "verdict" in df.columns:
                pivot = df.groupby(["probe_name", "verdict"]).size().unstack(fill_value=0)
                st.bar_chart(pivot)

            # Raw table
            with st.expander(f"Raw data (first {min(len(raw), 500)} rows)"):
                cols_show = [c for c in ["model_name", "probe_name", "depth", "trial", "verdict"] if c in df.columns]
                st.dataframe(df[cols_show], use_container_width=True, hide_index=True)
    else:
        st.info("No matrix results yet. Run the matrix above.")


# ════════════════════════════════════════════════════════════════════════════════
# Tab 3 — Analysis & Plots
# ════════════════════════════════════════════════════════════════════════════════

with tab_analysis:
    st.header("Analysis & Plots")
    st.write(
        "Aggregate `matrix.jsonl` into per-probe degradation curves and a summary CSV. "
        "Each plot shows pass-rate vs. context depth, one line per model."
    )

    if st.button("⚡ Generate Analysis", type="primary", disabled=not _api_ok):
        resp = _post("/analysis/run")
        if resp.status_code == 200:
            result = resp.json()
            st.success(f"Generated {len(result['plots'])} plot(s) and summary CSV.")
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.error(f"Error: {detail}")

    # Plots
    try:
        plots_resp = _get("/analysis/plots")
        plots: list[str] = plots_resp.json() if plots_resp.status_code == 200 else []
    except Exception:
        plots = []

    if plots:
        st.subheader("Degradation Curves")
        ncols = 2
        cols = st.columns(ncols)
        for i, name in enumerate(plots):
            with cols[i % ncols]:
                label = name.replace(".png", "").replace("_", " ").title()
                st.markdown(f"**{label}**")
                try:
                    img = _get(f"/analysis/plot/{name}")
                    if img.status_code == 200:
                        st.image(img.content, use_container_width=True)
                    else:
                        st.warning(f"Could not load {name}")
                except Exception as e:
                    st.warning(f"Error loading {name}: {e}")
    else:
        st.info("No plots yet. Click **Generate Analysis** above.")

    # Summary CSV
    st.divider()
    st.subheader("Summary CSV")
    try:
        csv_resp = _get("/analysis/csv")
        if csv_resp.status_code == 200:
            csv_text = csv_resp.text
            df = pd.read_csv(io.StringIO(csv_text))
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "⬇ Download summary.csv",
                data=csv_text,
                file_name="summary.csv",
                mime="text/csv",
            )
        else:
            st.info("No CSV yet. Run analysis first.")
    except Exception:
        st.info("No CSV yet. Run analysis first.")


# ════════════════════════════════════════════════════════════════════════════════
# Tab 4 — Probe Reference
# ════════════════════════════════════════════════════════════════════════════════

with tab_reference:
    st.header("Probe Reference")
    st.write("The 5 safety probes used in the experiment.")

    if AVAILABLE_PROBES:
        for p in AVAILABLE_PROBES:
            with st.expander(f"**{p['name']}**  —  _{p['failure_mode']}_", expanded=False):
                st.markdown(f"**Failure mode:** {p['failure_mode']}")
                st.markdown("**Rubric:**")
                st.text(p["rubric"])
    else:
        st.info("Connect to the API to see probe details.")
