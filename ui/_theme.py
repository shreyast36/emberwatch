"""Emberwatch theme — shared CSS + header components.

Every page imports this and calls `inject_theme()` once at the top.
Keeps the look-and-feel consistent across the landing page and sub-pages.
"""

import random

import streamlit as st


EMBERWATCH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');

/* ── Global base ──────────────────────────────────────────────────────── */
.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(196,18,18,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 50% 100%, rgba(255,87,34,0.12) 0%, transparent 60%),
        linear-gradient(180deg, #0a0606 0%, #050303 100%);
    color: #f0e8d8;
}

header[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

/* keep all real content above the ember field */
.stApp > div, section[data-testid="stSidebar"] { position: relative; z-index: 2; }

/* ── Headlines ────────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Cinzel', 'Georgia', serif;
    color: #ff7849;
    letter-spacing: 0.05em;
}

h1 {
    text-shadow: 0 0 20px rgba(255, 87, 34, 0.35);
    border-bottom: 1px solid #3a1a0a;
    padding-bottom: 0.4rem;
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #100706 0%, #0a0606 100%);
    border-right: 1px solid #3a1a0a;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] .stTitle {
    color: #ff5722 !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(180deg, #c41212 0%, #7a0a0a 100%);
    color: #fff5e6 !important;
    border: 1px solid #ff5722;
    border-radius: 3px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.85rem;
    padding: 0.55rem 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 0 12px rgba(255, 87, 34, 0.25), inset 0 1px 0 rgba(255,255,255,0.06);
}

.stButton > button:hover {
    background: linear-gradient(180deg, #ff5722 0%, #c41212 100%);
    box-shadow: 0 0 22px rgba(255, 87, 34, 0.55), inset 0 1px 0 rgba(255,255,255,0.1);
    transform: translateY(-1px);
}

.stButton > button:active { transform: translateY(0); }

/* ── Inputs ───────────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #150a08 !important;
    color: #f0e8d8 !important;
    border: 1px solid #5a2a1a !important;
    border-radius: 3px !important;
}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #ff5722 !important;
    box-shadow: 0 0 8px rgba(255, 87, 34, 0.4) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #3a1a0a;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #a89888;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    padding: 0.6rem 1.2rem;
    letter-spacing: 0.1em;
    font-size: 0.85rem;
    text-transform: uppercase;
}

.stTabs [aria-selected="true"] {
    color: #ff5722 !important;
    border-bottom: 2px solid #ff5722 !important;
    background: transparent !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #150a08, #0a0606);
    border: 1px solid #3a1a0a;
    border-radius: 4px;
    padding: 0.8rem 1rem;
}

[data-testid="stMetricValue"] {
    color: #ff5722 !important;
    font-family: 'Courier New', monospace !important;
}

/* ── Tables / dataframes ──────────────────────────────────────────────── */
.stDataFrame, .stTable {
    background: #100706;
    border: 1px solid #3a1a0a;
    border-radius: 3px;
}

/* ── Dividers ─────────────────────────────────────────────────────────── */
hr { border-color: #3a1a0a !important; opacity: 0.6; }

/* ── Status pills (top-right HUD) ─────────────────────────────────────── */
.ember-statusbar {
    position: fixed;
    top: 0.75rem;
    right: 1.25rem;
    display: flex;
    gap: 0.6rem;
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    z-index: 999;
}

.ember-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.3rem 0.7rem;
    border: 1px solid #5a2a1a;
    border-radius: 2px;
    background: rgba(10, 6, 6, 0.85);
    color: #ff5722;
    text-transform: uppercase;
    backdrop-filter: blur(4px);
}

.ember-dot { width: 6px; height: 6px; border-radius: 50%; }
.ember-dot-on  { background: #ff5722; box-shadow: 0 0 8px #ff5722;
                 animation: ember-pulse 2s ease-in-out infinite; }
.ember-dot-off { background: #5a2a1a; }

@keyframes ember-pulse {
    0%, 100% { opacity: 0.75; box-shadow: 0 0 6px #ff5722; }
    50%      { opacity: 1;    box-shadow: 0 0 14px #ff5722; }
}

/* ── EMBERWATCH hero title ────────────────────────────────────────────── */
.ember-title {
    font-family: 'Cinzel', 'Georgia', serif;
    font-size: clamp(3.5rem, 9vw, 6.5rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(180deg,
        #ffd9b0 0%, #ffb38a 18%, #ff7849 38%, #ff5722 58%, #c41212 80%, #5a1a0a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.18em;
    margin: 1rem 0 0 0;
    line-height: 1;
    filter: drop-shadow(0 0 25px rgba(255, 87, 34, 0.35));
    animation: ember-flicker 5s ease-in-out infinite;
}

@keyframes ember-flicker {
    0%, 100% { filter: drop-shadow(0 0 25px rgba(255, 87, 34, 0.35)) brightness(1); }
    47%      { filter: drop-shadow(0 0 35px rgba(255, 87, 34, 0.55)) brightness(1.08); }
    50%      { filter: drop-shadow(0 0 20px rgba(255, 87, 34, 0.25)) brightness(0.95); }
    53%      { filter: drop-shadow(0 0 38px rgba(255, 87, 34, 0.6))  brightness(1.12); }
}

.ember-tagline {
    text-align: center;
    color: #ff5722;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.55em;
    margin: 0.6rem 0 0.4rem 0;
    opacity: 0.85;
    text-transform: uppercase;
}

.ember-hr {
    width: 60%;
    margin: 1.2rem auto;
    border: 0;
    border-top: 1px solid #5a2a1a;
    position: relative;
}
.ember-hr::after {
    content: "◆";
    color: #ff5722;
    background: #050303;
    padding: 0 0.6rem;
    position: absolute;
    top: -0.7rem;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.8rem;
}

.ember-lede {
    text-align: center;
    font-family: 'Cinzel', 'Georgia', serif;
    font-size: 1.45rem;
    font-weight: 400;
    font-style: italic;
    letter-spacing: 0.04em;
    color: #d8c8b0;
    max-width: 820px;
    margin: 1.2rem auto 3rem;
    line-height: 1.5;
    text-shadow: 0 0 16px rgba(0, 0, 0, 0.6);
}

.ember-lede-em {
    background: linear-gradient(180deg, #ffd9b0 0%, #ff7849 45%, #ff5722 75%, #c41212 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-style: italic;
    letter-spacing: 0.06em;
    filter: drop-shadow(0 0 14px rgba(255, 87, 34, 0.45));
    animation: ember-flicker-soft 4.2s ease-in-out infinite;
}

/* ── Module cards ─────────────────────────────────────────────────────── */
.ember-card {
    background: linear-gradient(145deg, #1a0d0a 0%, #0a0606 100%);
    border: 1px solid #5a2a1a;
    border-radius: 4px;
    padding: 3rem 2rem 2.5rem 2rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.6), inset 0 0 40px rgba(255, 87, 34, 0.04);
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.ember-card::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 4px;
    padding: 1px;
    background: linear-gradient(135deg, transparent 40%, rgba(255, 87, 34, 0.4) 50%, transparent 60%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}

.ember-card:hover::before { opacity: 1; }

.ember-card:hover {
    border-color: #ff5722;
    box-shadow: 0 4px 28px rgba(255, 87, 34, 0.25), inset 0 0 50px rgba(255, 87, 34, 0.08);
    transform: translateY(-2px);
}

.ember-card-tag {
    color: #ff7849;
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    margin-bottom: 0.6rem;
    text-transform: uppercase;
    opacity: 0.7;
}

/* ── Cool fire-text title (the SLOWBURN / ALIGNGUARD text inside cards) ── */
.ember-firetext {
    font-family: 'Cinzel', 'Georgia', serif;
    font-size: 2.7rem;
    font-weight: 900;
    letter-spacing: 0.22em;
    text-align: center;
    margin: 0 0 0.6rem 0;
    line-height: 1.1;
    background: linear-gradient(180deg,
        #ffd9b0 0%, #ffb38a 15%, #ff7849 35%, #ff5722 55%, #c41212 78%, #5a1a0a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 12px rgba(255, 87, 34, 0.45));
    animation: ember-flicker-soft 3.6s ease-in-out infinite;
    text-transform: uppercase;
    position: relative;
}

@keyframes ember-flicker-soft {
    0%, 100% { filter: drop-shadow(0 0 12px rgba(255, 87, 34, 0.45)) brightness(1); }
    33%      { filter: drop-shadow(0 0 18px rgba(255, 87, 34, 0.65)) brightness(1.05); }
    66%      { filter: drop-shadow(0 0 10px rgba(255, 87, 34, 0.35)) brightness(0.97); }
}

.ember-card-sub {
    color: #ff7849;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    text-transform: uppercase;
    opacity: 0.8;
    font-family: 'Courier New', monospace;
}

.ember-card-desc {
    color: #d8c8b0;
    line-height: 1.65;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.ember-card-features {
    color: #a89888;
    font-size: 0.82rem;
    line-height: 1.8;
    border-top: 1px solid #3a1a0a;
    padding-top: 0.9rem;
    margin-top: 0.6rem;
    font-family: 'Courier New', monospace;
}

.ember-card-features b { color: #ff7849; font-weight: 700; }

/* ── Breadcrumb ───────────────────────────────────────────────────────── */
.ember-breadcrumb {
    font-family: 'Courier New', monospace;
    color: #a89888;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}
.ember-breadcrumb a { color: #ff7849; text-decoration: none; }
.ember-breadcrumb a:hover { color: #ff5722; }

/* ── Footer ───────────────────────────────────────────────────────────── */
.ember-footer {
    margin-top: 4rem;
    padding-top: 1.4rem;
    border-top: 1px solid #3a1a0a;
    text-align: center;
    color: #5a4a3a;
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
}
.ember-footer b { color: #ff5722; }

/* ── Ember particles (the simulated fire) ─────────────────────────────── */
.ember-field {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 1;
}

.ember-particle {
    position: absolute;
    bottom: -10px;
    border-radius: 50%;
    background: radial-gradient(circle,
        #fff5e0 0%, #ffb38a 20%, #ff7849 40%, #ff5722 60%, #c41212 80%, transparent 100%);
    filter: blur(0.4px);
    animation: ember-rise linear infinite;
    will-change: transform, opacity;
}

@keyframes ember-rise {
    0% {
        transform: translateY(0) translateX(0) scale(1);
        opacity: 0;
    }
    6%  { opacity: 1; }
    35% { transform: translateY(-30vh) translateX(calc(var(--drift) * 0.4)) scale(0.95); }
    70% { transform: translateY(-65vh) translateX(calc(var(--drift) * 0.8)) scale(0.7); opacity: 0.8; }
    100% {
        transform: translateY(-110vh) translateX(var(--drift)) scale(0.4);
        opacity: 0;
    }
}

/* Heat haze at the very bottom of the page */
.ember-heatwave {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    height: 35vh;
    background: linear-gradient(0deg,
        rgba(196, 18, 18, 0.15) 0%,
        rgba(255, 87, 34, 0.06) 40%,
        transparent 100%);
    pointer-events: none;
    z-index: 1;
    animation: ember-haze 8s ease-in-out infinite;
}

@keyframes ember-haze {
    0%, 100% { opacity: 0.85; }
    50%      { opacity: 1; }
}
</style>
"""


def _ember_field_html(count: int = 55) -> str:
    """Build a deterministic field of rising ember particles."""
    random.seed(7)
    particles = []
    for _ in range(count):
        left = random.uniform(0, 100)
        size = random.uniform(2, 5)
        duration = random.uniform(6, 14)
        delay = random.uniform(0, duration)
        drift = random.uniform(-40, 40)
        opacity = random.uniform(0.5, 1.0)
        particles.append(
            f'<span class="ember-particle" style="'
            f'left:{left:.1f}%; '
            f'width:{size:.1f}px; height:{size:.1f}px; '
            f'animation-duration:{duration:.1f}s; '
            f'animation-delay:-{delay:.1f}s; '
            f'opacity:{opacity:.2f}; '
            f'--drift:{drift:.1f}px;"></span>'
        )
    return (
        '<div class="ember-field">'
        + ''.join(particles)
        + '</div>'
        + '<div class="ember-heatwave"></div>'
    )


def inject_theme() -> None:
    """Inject Emberwatch CSS + the animated ember particle field."""
    st.markdown(EMBERWATCH_CSS, unsafe_allow_html=True)
    st.markdown(_ember_field_html(), unsafe_allow_html=True)


def status_bar(api_ok: bool) -> None:
    """Top-right HUD status pill. Call after inject_theme()."""
    dot = "ember-dot-on" if api_ok else "ember-dot-off"
    label = "ONLINE" if api_ok else "OFFLINE"
    st.markdown(
        f"""
        <div class="ember-statusbar">
            <div class="ember-pill"><span class="ember-dot {dot}"></span>{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def breadcrumb(module: str) -> None:
    """Sub-page nav breadcrumb. e.g. breadcrumb('Slowburn') prints `EMBERWATCH › SLOWBURN`."""
    st.markdown(
        f'<div class="ember-breadcrumb">▸ EMBERWATCH &nbsp;›&nbsp; <b style="color:#ff5722">{module.upper()}</b></div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    """Standard footer."""
    st.markdown(
        '<div class="ember-footer"><b>EMBERWATCH</b> &nbsp;·&nbsp; OBSERVE · ANTICIPATE · PREVENT &nbsp;·&nbsp; v0.1</div>',
        unsafe_allow_html=True,
    )
