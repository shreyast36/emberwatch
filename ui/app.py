"""Landing page — routes user to SlowBurn or AlignGuard."""

import os
import requests
import streamlit as st

API_URL = os.environ.get("SLOWBURN_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="LLM Safety Toolkit",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── API health check (small badge in corner) ───────────────────────────────────
try:
    r = requests.get(f"{API_URL}/health", timeout=2)
    _api_ok = r.status_code == 200
except Exception:
    _api_ok = False

with st.sidebar:
    st.caption(f"API: {'🟢 online' if _api_ok else '🔴 offline'}")
    st.caption(f"Endpoint: {API_URL}")

# ── Hero ───────────────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='text-align:center; margin-bottom:0'>🛡️ LLM Safety Toolkit</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:gray; margin-top:4px'>"
    "Choose a tool to get started</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Tool cards ─────────────────────────────────────────────────────────────────

col_sb, col_ag = st.columns(2, gap="large")

with col_sb:
    st.markdown("### 🔥 SlowBurn")
    st.markdown(
        "**Context Degradation Testing**\n\n"
        "Stress-test an LLM's safety properties as conversation context grows. "
        "Run baseline validation, a full model × probe × depth matrix, and generate "
        "degradation curve charts to spot where safety breaks down."
    )
    st.markdown("")
    st.markdown("**Features**")
    st.markdown(
        "- Multi-model support (Claude, GPT, Gemini, Grok)\n"
        "- Configurable filler corpus (trivia / coding Q&A)\n"
        "- Automated baseline consistency checking\n"
        "- Per-probe degradation curve plots\n"
        "- Resumable matrix runs via JSONL"
    )
    st.markdown("")
    if st.button("Launch SlowBurn →", type="primary", use_container_width=True, key="go_sb"):
        st.switch_page("pages/1_Slowburn.py")

with col_ag:
    st.markdown("### 🛡️ AlignGuard")
    st.markdown(
        "**Multi-Agent Alignment Monitoring**\n\n"
        "Monitor a 4-agent customer-support pipeline for alignment failures. "
        "Detects spec gaming, deceptive reasoning, canary probe failures, and "
        "score drift — then generates per-session introspection reports."
    )
    st.markdown("")
    st.markdown("**Features**")
    st.markdown(
        "- Gaming Detector, Reasoning Auditor, Canary Prober, Drift Tracker\n"
        "- LLM-powered prompt weakness analysis\n"
        "- Per-session markdown introspection reports\n"
        "- Multi-session alignment trend charts\n"
        "- Risk-level alerts (LOW → CRITICAL)"
    )
    st.markdown("")
    if st.button("Launch AlignGuard →", type="primary", use_container_width=True, key="go_ag"):
        st.switch_page("pages/2_AlignGuard.py")

st.divider()
st.caption(
    "SlowBurn measures LLM safety degradation over growing context. "
    "AlignGuard monitors agentic pipelines for alignment failures in real time."
)
