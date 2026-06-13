"""
dashboard.py
------------
Entry point for NeuralWatch.

Run with:
    streamlit run dashboard.py

Layers:
  1 - Biometric gesture lock      (gesture_lock.py)
  2 - Neuromorphic drift detector (neural_brain.py)
  3 - Cryptographic audit chain   (neuralwatch.py)

Theme: dark, cyan-accent UI matching the NeuralWatch demo video
(Vector Vision). Colors and layout are also set in
.streamlit/config.toml.
"""

import time
import pandas as pd
import streamlit as st

from neural_brain import NeuromorphicBrain
from neuralwatch import NeuralWatch, DRIFT_THRESHOLD, SPIKE_THRESHOLD
from gesture_lock import run_gesture_authentication_ui

st.set_page_config(
    page_title="NeuralWatch",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS — dark theme polish matching the demo video
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0B0F19; }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #11182A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="stMetric"] label {
        color: #38BDF8 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #67E8F9 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19;
        border-right: 1px solid #1E293B;
    }

    /* Headings */
    h1, h2, h3 { color: #E2E8F0; }

    /* Status banners */
    .nw-banner-safe {
        background-color: rgba(34,197,94,0.08);
        border: 1px solid #16A34A;
        color: #4ADE80;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        margin-bottom: 6px;
    }
    .nw-banner-warning {
        background-color: rgba(234,179,8,0.08);
        border: 1px solid #CA8A04;
        color: #FACC15;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        margin-bottom: 6px;
    }
    .nw-banner-spike {
        background-color: rgba(239,68,68,0.08);
        border: 1px solid #DC2626;
        color: #F87171;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        margin-bottom: 6px;
    }
    .nw-spike-fired {
        background-color: #7F1D1D;
        color: #FECACA;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 16px;
    }

    /* Audit log entries */
    .nw-log-safe   { color: #4ADE80; font-family: 'Courier New', monospace; font-size: 0.85rem; }
    .nw-log-spike  { color: #F87171; font-family: 'Courier New', monospace; font-size: 0.85rem; }
    .nw-log-warn   { color: #FACC15; font-family: 'Courier New', monospace; font-size: 0.85rem; }
    .nw-log-roll   { color: #67E8F9; font-family: 'Courier New', monospace; font-size: 0.85rem; }

    /* Authenticated badge */
    .nw-auth-badge {
        background-color: rgba(34,197,94,0.12);
        border: 1px solid #16A34A;
        color: #4ADE80;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "brain" not in st.session_state:
    st.session_state.brain = NeuromorphicBrain()

if "watch" not in st.session_state:
    st.session_state.watch = NeuralWatch(st.session_state.brain)

if "tick" not in st.session_state:
    st.session_state.tick = 0

if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: tick, drift, membrane, status

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "attack_mode" not in st.session_state:
    st.session_state.attack_mode = False

if "session_started" not in st.session_state:
    st.session_state.session_started = time.strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Layer 1 - Gesture lock gate
# ---------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(
            """
            <div style="
                background-color:#11182A;
                border:1px solid #1E293B;
                border-radius:14px;
                padding:48px 40px;
                text-align:center;
            ">
                <div style="font-size:3.5rem; line-height:1;">🧠</div>
                <h1 style="color:#22D3EE; margin-top:12px; margin-bottom:4px;">NeuralWatch</h1>
                <p style="color:#94A3B8; margin:2px 0;">Neuromorphic AI Integrity Monitor</p>
                <p style="color:#64748B; margin:2px 0 18px 0; font-size:0.9rem;">
                    Layer 1 — Biometric Authentication Required
                </p>
                <hr style="border-color:#1E293B; margin:18px 0;">
                <p style="color:#94A3B8; font-size:0.9rem; margin:0;">
                    To unlock: perform the authorized hand gesture<br>
                    in front of your webcam, or use demo bypass below.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True)

        if run_gesture_authentication_ui(st):
            st.session_state.authenticated = True
            st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# Main dashboard (post-authentication)
# ---------------------------------------------------------------------------
brain = st.session_state.brain
watch = st.session_state.watch

# --- Sidebar: Control Panel --------------------------------------------------
with st.sidebar:
    st.markdown("## Control Panel")
    st.markdown("---")

    st.session_state.attack_mode = st.toggle(
        "🧬 Simulate Attacker",
        value=st.session_state.attack_mode,
        help="Slowly poisons the neural weights to simulate a real adversarial attack",
    )

    if st.session_state.attack_mode:
        st.markdown(
            "<div style='background-color:rgba(239,68,68,0.08); border:1px solid #DC2626; "
            "color:#F87171; border-radius:8px; padding:10px 14px; font-size:0.85rem;'>"
            "⚠️ Attacker active — slowly poisoning neural weights</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background-color:rgba(34,197,94,0.08); border:1px solid #16A34A; "
            "color:#4ADE80; border-radius:8px; padding:10px 14px; font-size:0.85rem;'>"
            "✓ No active attack detected</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if not st.session_state.monitoring:
            if st.button("▶ Start", use_container_width=True, type="primary"):
                st.session_state.monitoring = True
                st.rerun()
        else:
            st.button("▶ Start", use_container_width=True, disabled=True)
    with col_b:
        if st.session_state.monitoring:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state.monitoring = False
                st.rerun()
        else:
            st.button("⏸ Pause", use_container_width=True, disabled=True)

    if st.button("🔄 Rollback Brain", use_container_width=True):
        watch.perform_rollback()
        st.success("Brain rolled back to clean state!")

    st.markdown("---")
    st.markdown("### Layer 3 — Audit Integrity")

    if st.button("🔍 Verify Log Chain", use_container_width=True):
        if watch.verify_log_integrity():
            st.success("Log chain verified — no tampering detected")
        else:
            st.markdown(
                "<div style='background-color:rgba(239,68,68,0.12); border:1px solid #DC2626; "
                "color:#FCA5A5; border-radius:8px; padding:10px 14px; font-size:0.85rem; "
                "font-weight:600;'>🔓 TAMPER DETECTED — Log chain broken!</div>",
                unsafe_allow_html=True,
            )

    if st.button("🔓 Simulate Tamper Attack", use_container_width=True):
        watch.simulate_tamper()
        st.warning("Last log entry tampered with (drift hidden)")

    st.markdown("---")
    if st.button("🔒 Lock Dashboard", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.monitoring = False
        st.rerun()

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
    st.caption(f"Session started: {st.session_state.session_started}")
    st.caption(f"Log entries: {len(watch.audit_log)}")
    st.caption(f"Rollbacks performed: {watch.rollback_count}")


# --- Header -------------------------------------------------------------------
header_l, header_r = st.columns([4, 1])
with header_l:
    st.markdown(
        "<div style='display:flex; align-items:center; gap:12px;'>"
        "<div style='font-size:2.2rem;'>🧠</div>"
        "<div>"
        "<h1 style='margin:0; color:#22D3EE;'>NeuralWatch</h1>"
        "<p style='margin:0; color:#94A3B8;'>Neuromorphic AI Integrity Monitor — All systems online</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )
with header_r:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<span class='nw-auth-badge'>● AUTHENTICATED</span>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1E293B; margin-top:10px;'>", unsafe_allow_html=True)

# --- Top metrics -------------------------------------------------------------
drift = brain.get_drift_score()
membrane = round(brain.membrane_potential, 4)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Neural Drift Score", f"{drift:.4f}")
    st.caption(f"↑ threshold: {DRIFT_THRESHOLD}")
with m2:
    st.metric("Membrane Potential", f"{membrane:.4f}")
    st.caption(f"↑ spike at: {SPIKE_THRESHOLD}")
with m3:
    st.metric("Total Spikes Fired", watch.total_spikes)
with m4:
    st.metric("Rollbacks Performed", watch.rollback_count)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# --- Status banner -------------------------------------------------------------
last_status = st.session_state.history[-1]["status"] if st.session_state.history else "SAFE"

if last_status == "SPIKE":
    st.markdown(
        f"<div class='nw-banner-spike'>⚠ NEUROMORPHIC SPIKE DETECTED &nbsp;|&nbsp; "
        f"Drift: {drift:.5f} &nbsp;|&nbsp; LIF threshold crossed — CONFIRMED POISONING ATTACK<br>"
        f"Rollback recommended immediately</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='nw-spike-fired'>⚡ NEUROMORPHIC SPIKE FIRED ⚡</div>",
        unsafe_allow_html=True,
    )
elif last_status == "WARNING":
    st.markdown(
        f"<div class='nw-banner-warning'>⚠ WARNING — Drift approaching threshold &nbsp;|&nbsp; "
        f"Drift: {drift:.5f} &nbsp;|&nbsp; Monitor closely</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<div class='nw-banner-safe'>✓ SAFE — Normal neuromorphic learning &nbsp;|&nbsp; "
        f"Drift: {drift:.5f} &nbsp;|&nbsp; No anomalies detected</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# --- Charts -------------------------------------------------------------------
chart_l, chart_r = st.columns(2)

with chart_l:
    st.markdown("### Neural Drift Over Time")
    st.caption("Safe zone: below 0.12 | Warning: 0.12–0.15 | Spike fires: above 0.15")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df = df.set_index("tick")
        df["Safe Limit"] = DRIFT_THRESHOLD
        df["Spike Threshold"] = SPIKE_THRESHOLD
        st.line_chart(
            df[["drift", "Safe Limit", "Spike Threshold"]],
            color=["#22D3EE", "#4ADE80", "#F87171"],
            height=280,
        )
    else:
        st.markdown(
            "<div style='height:280px; border:1px solid #1E293B; border-radius:8px; "
            "display:flex; align-items:flex-end; padding:8px; color:#475569;'>0</div>",
            unsafe_allow_html=True,
        )

with chart_r:
    st.markdown("### LIF Membrane Potential")
    st.caption("Neuromorphic spike model — resets to 0 after firing")
    if st.session_state.history:
        df2 = pd.DataFrame(st.session_state.history).set_index("tick")
        st.line_chart(df2[["membrane"]], color=["#F87171"], height=280)
    else:
        st.markdown(
            "<div style='height:280px; border:1px solid #1E293B; border-radius:8px; "
            "display:flex; align-items:flex-end; padding:8px; color:#475569;'>0</div>",
            unsafe_allow_html=True,
        )

st.markdown("<hr style='border-color:#1E293B;'>", unsafe_allow_html=True)

# --- Audit log -----------------------------------------------------------------
st.markdown("### Live Audit Log — Cryptographically Signed")

if watch.audit_log:
    for entry in reversed(watch.audit_log[-12:]):
        status = entry.get("status", "")
        sig = entry.get("signature", "")
        if status == "SPIKE":
            css = "nw-log-spike"
            icon = "⚡ ATK  ★SPIKE"
        elif status == "ROLLBACK":
            css = "nw-log-roll"
            icon = ""
        elif status == "WARNING":
            css = "nw-log-warn"
            icon = "⚡ ATK" if entry.get("attack_mode") else ""
        else:
            css = "nw-log-safe"
            icon = "⚡ ATK" if entry.get("attack_mode") else ""

        line = (
            f"[{entry.get('time','')}] {entry.get('tick',''):<10} "
            f"STATUS:{status:<10} DRIFT:{entry.get('drift',0):.5f}  "
            f"MEM:{entry.get('membrane',0):.4f}    {icon}    SIG:{sig}"
        )
        st.markdown(f"<div class='{css}'>{line}</div>", unsafe_allow_html=True)
else:
    st.caption("No log entries yet — click Start to begin monitoring.")


# ---------------------------------------------------------------------------
# Monitoring loop (one tick per rerun while monitoring is True)
# ---------------------------------------------------------------------------
if st.session_state.monitoring:
    st.session_state.tick += 1
    tick = st.session_state.tick

    if st.session_state.attack_mode:
        brain.receive_poison()
    else:
        brain.learn_normally()

    result = watch.monitor_tick(tick, st.session_state.attack_mode)

    st.session_state.history.append({
        "tick": tick,
        "drift": result["drift"],
        "membrane": result["membrane"],
        "status": result["status"],
        "time": result["log_entry"]["time"],
        "attack_mode": st.session_state.attack_mode,
    })

    time.sleep(1)
    st.rerun()
