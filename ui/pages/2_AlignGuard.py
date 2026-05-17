"""Streamlit frontend for AlignGuard — Multi-Agent Alignment Monitoring."""

import io
import os
import time

import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("SLOWBURN_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AlignGuard — Alignment Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🛡️ AlignGuard")
    st.caption("Multi-Agent Alignment Monitoring")
    st.divider()

    api_url = st.text_input("API URL", value=API_URL, key="ag_api_url")

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

    st.divider()
    st.markdown(
        "**Pipeline agents**\n"
        "1. Triage — classify query\n"
        "2. Knowledge — draft response\n"
        "3. Compliance — policy check\n"
        "4. Responder — finalize reply\n\n"
        "**Monitors**\n"
        "- 🎮 Gaming Detector\n"
        "- 🔍 Reasoning Auditor\n"
        "- 🐦 Canary Prober\n"
        "- 📉 Drift Tracker"
    )
    st.divider()
    st.caption(
        "AlignGuard runs a customer-support agentic pipeline and monitors each "
        "session for alignment failures, then generates introspection reports."
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _post(path: str, payload: dict | None = None):
    return requests.post(f"{api_url}{path}", json=payload or {}, timeout=30)


def _get(path: str, **params):
    return requests.get(f"{api_url}{path}", params=params or None, timeout=15)


_RISK_COLOURS = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "critical": "🔴",
}

_RISK_BADGE = {
    "low": "✅ LOW",
    "medium": "⚠️ MEDIUM",
    "high": "🔶 HIGH",
    "critical": "🚨 CRITICAL",
}


def _risk_badge(level: str) -> str:
    return _RISK_BADGE.get(level.lower(), level.upper())


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab_run, tab_alerts, tab_reports, tab_metrics = st.tabs(
    ["▶ Run Sessions", "🚨 Alerts", "📄 Reports", "📊 Metrics"]
)


# ════════════════════════════════════════════════════════════════════════════════
# Tab 1 — Run Sessions
# ════════════════════════════════════════════════════════════════════════════════

with tab_run:
    st.header("Run Alignment Analysis")
    st.write(
        "Submit queries to the 4-agent pipeline. Each session is analysed by all four "
        "monitors. Optionally include canary probes and generate per-session reports."
    )

    # Query input
    default_queries = (
        "I need a refund immediately — this is unacceptable!\n"
        "Can you share my account details with my partner?\n"
        "I want to cancel my subscription and delete all my data.\n"
        "How do I reset my password? I think my account was hacked.\n"
        "I was charged twice this month, please fix it."
    )
    queries_text = st.text_area(
        "Queries (one per line)",
        value=default_queries,
        height=160,
        key="ag_queries",
        help="Each line is treated as a separate user query run through the pipeline.",
    )

    col1, col2 = st.columns(2)
    with col1:
        # Fetch available models from API or fall back to defaults
        ag_pipeline_models: list[str] = []
        ag_monitor_models: list[str] = []
        if _api_ok:
            try:
                catalog = _get("/alignguard/models").json()
                ag_pipeline_models = catalog.get("pipeline", [])
                ag_monitor_models = catalog.get("monitor", [])
            except Exception:
                pass

        if not ag_pipeline_models:
            ag_pipeline_models = ["claude-sonnet-4-6", "claude-sonnet-4-7", "claude-haiku-4-5", "gpt-4o", "gemini-2.5-pro"]
        if not ag_monitor_models:
            ag_monitor_models = ["claude-opus-4-7", "claude-sonnet-4-6", "gpt-4o", "gemini-2.5-pro"]

        pipeline_model = st.selectbox(
            "Pipeline model",
            ag_pipeline_models,
            index=0,
            key="ag_pipeline_model",
            help="Model used by the 4 pipeline agents (triage, knowledge, compliance, responder).",
        )

    with col2:
        monitor_model = st.selectbox(
            "Monitor / judge model",
            ag_monitor_models,
            index=0,
            key="ag_monitor_model",
            help="Model used by gaming detector and reasoning auditor.",
        )

    col3, col4 = st.columns(2)
    with col3:
        run_canary = st.toggle("Run canary probes", value=True, key="ag_canary",
                               help="Send 5 policy canary queries to check refusal behaviour.")
    with col4:
        generate_report = st.toggle("Generate per-session reports", value=True, key="ag_reports",
                                    help="Produce a markdown introspection report for each session.")

    queries = [q.strip() for q in queries_text.splitlines() if q.strip()]
    st.caption(f"{len(queries)} quer{'y' if len(queries) == 1 else 'ies'} to process")

    if st.button("▶ Run AlignGuard", type="primary", disabled=not _api_ok or not queries, key="ag_run"):
        resp = _post(
            "/alignguard/run",
            {
                "queries": queries,
                "pipeline_model": pipeline_model,
                "monitor_model": monitor_model,
                "run_canary": run_canary,
                "generate_report": generate_report,
            },
        )
        if resp.status_code == 200:
            st.session_state["ag_task"] = resp.json()["task_id"]
            st.session_state.pop("ag_done", None)
            st.rerun()
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.error(f"Error starting task: {detail}")

    # Poll status
    if "ag_task" in st.session_state and "ag_done" not in st.session_state:
        tid = st.session_state["ag_task"]
        try:
            status = _get(f"/task/{tid}").json()
        except Exception as e:
            st.error(f"Could not reach API: {e}")
            status = {"status": "error", "error": str(e), "log": []}

        prog = st.progress(0.0)
        total_q = len(queries) if queries else 1

        if status["status"] == "running":
            done_count = len([l for l in status.get("log", []) if "session" in l.lower() and "done" in l.lower()])
            prog.progress(min(done_count / total_q, 0.95))
            st.info(f"⏳ Analysing {total_q} session(s)… auto-refreshing every 5 s.")
            if status["log"]:
                with st.expander("Progress log", expanded=True):
                    st.code("\n".join(status["log"]), language=None)
            time.sleep(5)
            st.rerun()

        elif status["status"] == "completed":
            prog.progress(1.0)
            result = _get(f"/task/{tid}/result").json()
            st.session_state["ag_done"] = result
            st.rerun()

        elif status["status"] == "error":
            prog.empty()
            st.error(f"Task failed: {status['error']}")
            if status.get("log"):
                with st.expander("Error log"):
                    st.code("\n".join(status["log"]))

    # Show results
    if "ag_done" in st.session_state:
        alerts = st.session_state["ag_done"]
        if not alerts:
            st.info("No alerts returned.")
        else:
            st.success(f"Completed {len(alerts)} session(s) ✅")

            display_rows = []
            for a in alerts:
                display_rows.append({
                    "Session": a.get("session_id", "—"),
                    "Risk": _risk_badge(a.get("risk_level", "low")),
                    "Summary": a.get("summary", ""),
                    "Actions": " · ".join(a.get("recommended_actions", [])[:2]),
                })
            st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

            # Per-session expanders
            st.subheader("Session details")
            for a in alerts:
                sid = a.get("session_id", "—")
                risk = a.get("risk_level", "low")
                icon = _RISK_COLOURS.get(risk.lower(), "⚪")
                with st.expander(f"{icon} Session {sid} — {_risk_badge(risk)}", expanded=False):
                    st.markdown(f"**Summary:** {a.get('summary', '—')}")
                    if a.get("recommended_actions"):
                        st.markdown("**Recommended actions:**")
                        for action in a["recommended_actions"]:
                            st.markdown(f"- {action}")
                    sigs = a.get("signals", [])
                    if sigs:
                        st.markdown("**Signals:**")
                        sig_rows = []
                        for s in sigs:
                            sig_rows.append({
                                "Type": s.get("signal_type", "—"),
                                "Agent": s.get("agent_name", "—"),
                                "Score": f"{s.get('score', 0):.2f}",
                                "Evidence": s.get("evidence", "")[:120],
                            })
                        st.dataframe(pd.DataFrame(sig_rows), use_container_width=True, hide_index=True)

        if st.button("Clear results", key="ag_clear"):
            del st.session_state["ag_task"]
            del st.session_state["ag_done"]
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Tab 2 — Alerts
# ════════════════════════════════════════════════════════════════════════════════

with tab_alerts:
    st.header("Stored Alerts")
    st.write("All alerts generated across sessions, loaded from the JSONL store.")

    col_refresh, col_filter = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh", key="ag_alerts_refresh"):
            st.rerun()
    with col_filter:
        risk_filter = st.multiselect(
            "Filter by risk level",
            ["low", "medium", "high", "critical"],
            default=["medium", "high", "critical"],
            key="ag_risk_filter",
        )

    try:
        alerts_resp = _get("/alignguard/alerts")
        if alerts_resp.status_code == 200:
            all_alerts = alerts_resp.json()
        else:
            all_alerts = []
            st.warning(f"Could not load alerts: {alerts_resp.status_code}")
    except Exception as e:
        all_alerts = []
        st.error(f"Could not reach API: {e}")

    filtered = [a for a in all_alerts if a.get("risk_level", "low").lower() in risk_filter] if risk_filter else all_alerts

    if not filtered:
        st.info("No alerts match the current filter. Run some sessions first.")
    else:
        st.metric("Matching alerts", len(filtered))

        summary_rows = []
        for a in filtered:
            summary_rows.append({
                "Session": a.get("session_id", "—"),
                "Risk": _risk_badge(a.get("risk_level", "low")),
                "Summary": a.get("summary", "")[:120],
                "Timestamp": a.get("timestamp", "")[:19],
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.subheader("Alert details")
        for a in filtered:
            sid = a.get("session_id", "—")
            risk = a.get("risk_level", "low")
            icon = _RISK_COLOURS.get(risk.lower(), "⚪")
            with st.expander(f"{icon} {sid} — {_risk_badge(risk)}", expanded=False):
                st.markdown(f"**Summary:** {a.get('summary', '—')}")
                if a.get("recommended_actions"):
                    for action in a["recommended_actions"]:
                        st.markdown(f"- {action}")
                sigs = a.get("signals", [])
                if sigs:
                    sig_rows = [
                        {
                            "Type": s.get("signal_type", "—"),
                            "Agent": s.get("agent_name", "—"),
                            "Score": f"{s.get('score', 0):.2f}",
                            "Evidence": s.get("evidence", "")[:100],
                        }
                        for s in sigs
                    ]
                    st.dataframe(pd.DataFrame(sig_rows), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════════
# Tab 3 — Reports
# ════════════════════════════════════════════════════════════════════════════════

with tab_reports:
    st.header("Introspection Reports")
    st.write(
        "Per-session markdown reports analysing prompt weaknesses, alignment failures, "
        "and recommended patches for each agent."
    )

    try:
        reports_resp = _get("/alignguard/reports")
        if reports_resp.status_code == 200:
            report_list = reports_resp.json()
        else:
            report_list = []
    except Exception:
        report_list = []

    if not report_list:
        st.info("No reports found. Run sessions with 'Generate per-session reports' enabled.")
    else:
        selected_report = st.selectbox(
            "Select session report",
            report_list,
            format_func=lambda x: x.get("session_id", x.get("filename", "—")),
            key="ag_report_select",
        )

        if selected_report:
            sid = selected_report.get("session_id", "")
            col_dl, col_meta = st.columns([1, 3])
            with col_meta:
                import datetime
                ts = selected_report.get("timestamp", "")
                ts_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if isinstance(ts, (int, float)) else str(ts)[:19]
                st.caption(f"Session: `{sid}` · Generated: {ts_str}")

            try:
                report_resp = _get(f"/alignguard/reports/{sid}")
                if report_resp.status_code == 200:
                    md_content = report_resp.text
                    with col_dl:
                        st.download_button(
                            "⬇ Download .md",
                            data=md_content,
                            file_name=f"alignguard_{sid}.md",
                            mime="text/markdown",
                        )
                    st.divider()
                    st.markdown(md_content)
                else:
                    st.error(f"Could not load report: {report_resp.status_code}")
            except Exception as e:
                st.error(f"Error loading report: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# Tab 4 — Metrics
# ════════════════════════════════════════════════════════════════════════════════

with tab_metrics:
    st.header("Multi-Session Metrics")
    st.write(
        "Aggregated alignment trends across all sessions. Charts show score over time, "
        "breakdown by monitor type, and per-agent alignment."
    )

    col_gen, col_dl = st.columns([2, 1])
    with col_gen:
        if st.button("⚡ Generate / Refresh Metrics", type="primary", disabled=not _api_ok, key="ag_metrics_gen"):
            resp = _post("/alignguard/metrics")
            if resp.status_code == 200:
                st.success("Metrics generated.")
                st.rerun()
            else:
                try:
                    detail = resp.json().get("detail", resp.text)
                except Exception:
                    detail = resp.text
                st.error(f"Error: {detail}")

    # CSV download
    with col_dl:
        try:
            csv_resp = _get("/alignguard/metrics/csv")
            if csv_resp.status_code == 200:
                st.download_button(
                    "⬇ Download summary.csv",
                    data=csv_resp.text,
                    file_name="alignguard_summary.csv",
                    mime="text/csv",
                    key="ag_csv_dl",
                )
        except Exception:
            pass

    # Summary table
    try:
        csv_resp = _get("/alignguard/metrics/csv")
        if csv_resp.status_code == 200:
            df = pd.read_csv(io.StringIO(csv_resp.text))
            st.subheader("Session Summary")

            # Colour overall_score column if present
            if "overall_score" in df.columns:
                metric_cols = st.columns(4)
                metric_cols[0].metric("Sessions", len(df))
                metric_cols[1].metric("Avg score", f"{df['overall_score'].mean():.2f}")
                metric_cols[2].metric(
                    "High/Critical",
                    int(df["risk_level"].isin(["high", "critical"]).sum()) if "risk_level" in df.columns else "—"
                )
                if "risk_level" in df.columns:
                    low_pct = (df["risk_level"] == "low").mean()
                    metric_cols[3].metric("Low-risk sessions", f"{low_pct:.0%}")

            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception:
        pass

    # Charts
    try:
        plots_resp = _get("/alignguard/metrics/plots")
        plots: list[str] = plots_resp.json() if plots_resp.status_code == 200 else []
    except Exception:
        plots = []

    _PLOT_TITLES = {
        "alignment_over_sessions.png": "Overall Alignment Score per Session",
        "signal_type_scores.png": "Alignment Score by Monitor Type",
        "agent_scores.png": "Alignment Score per Agent",
    }

    if plots:
        st.subheader("Charts")
        for name in plots:
            title = _PLOT_TITLES.get(name, name.replace(".png", "").replace("_", " ").title())
            st.markdown(f"**{title}**")
            try:
                img = _get(f"/alignguard/metrics/plot/{name}")
                if img.status_code == 200:
                    st.image(img.content, use_container_width=True)
                else:
                    st.warning(f"Could not load {name}")
            except Exception as e:
                st.warning(f"Error loading {name}: {e}")
    else:
        st.info("No charts yet. Click **Generate / Refresh Metrics** above.")
