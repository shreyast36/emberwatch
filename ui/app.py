"""Emberwatch — landing. Routes to Slowburn or AlignGuard."""

import os
import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from _theme import inject_theme, status_bar, footer  # noqa: E402

API_URL = os.environ.get("SLOWBURN_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Emberwatch",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_theme()

try:
    _api_ok = requests.get(f"{API_URL}/health", timeout=2).status_code == 200
except Exception:
    _api_ok = False

status_bar(_api_ok)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="height: 4rem;"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="ember-title">EMBERWATCH</h1>', unsafe_allow_html=True)
st.markdown('<div class="ember-tagline">Observe · Anticipate · Prevent</div>', unsafe_allow_html=True)
st.markdown('<hr class="ember-hr">', unsafe_allow_html=True)
st.markdown(
    '<div style="display:flex; justify-content:center; width:100%;">'
    '<p class="ember-lede">'
    'AI safety, <span class="ember-lede-em">beyond the benchmark.</span>'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Modules ────────────────────────────────────────────────────────────────────
col_sb, col_ag = st.columns(2, gap="large")

with col_sb:
    st.markdown(
        """
        <div class="ember-card">
            <div class="ember-firetext">SLOWBURN</div>
            <div class="ember-card-sub">Context Degradation Testing</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("ENTER  SLOWBURN  →", type="primary", use_container_width=True, key="go_sb"):
        st.switch_page("pages/1_Slowburn.py")

with col_ag:
    st.markdown(
        """
        <div class="ember-card">
            <div class="ember-firetext">ALIGNGUARD</div>
            <div class="ember-card-sub">Multi-Agent Alignment Monitoring</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("ENTER  ALIGNGUARD  →", type="primary", use_container_width=True, key="go_ag"):
        st.switch_page("pages/2_AlignGuard.py")

footer()
