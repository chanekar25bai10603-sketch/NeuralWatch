"""
dashboard.py
------------
NeuralWatch — Main Dashboard
Run with: streamlit run dashboard.py

This is the full MVP combining all three layers:
  Layer 1 — Gesture biometric lock
  Layer 2 — Live neural drift detection with LIF spike model
  Layer 3 — Cryptographic tamper-evident audit log

For the demo video, run this file and follow the scenes.
"""

import streamlit as st
import pandas as pd
import time
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from neural_brain import NeuromorphicBrain
from neuralwatch import NeuralWatch

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NeuralWatch",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — dark cyber look
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0a0e1a; color: #e0e6f0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0d1220; border-right: 1px solid #1e2a40; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #0d1220;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 12px;
    }
    [data-testid="stMetricValue"] { color: #4dd8ff; font-size: 2rem !important; }
    [data-testid="stMetricLabel"] { color: #7a9bbf; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem; }

    /* Headers */
    h1, h2, h3 { color: #a0cfff; }

    /* Alert boxes */
    .alert-safe {
        background: #0a2a1a; border: 1px solid #1a6b3a;
        border-radius: 8px; padding: 12px 16px;
        color: #4dff91; font-family: monospace; font-size: 14px;
    }
    .alert-warning {
        background: #2a1a00; border: 1px solid #8b6000;
        border-radius: 8px; padding: 12px 16px;
        color: #ffcc44; font-family: monospace; font-size: 14px;
    }
    .alert-danger {
        background: #2a0a0a; border: 1px solid #8b0000;
        border-radius: 8px; padding: 12px 16px;
        color: #ff4444; font-family: monospace; font-size: 14px;
        animation: pulse 1s infinite;
    }
    .alert-rollback {
        background: #1a1a2a; border: 1px solid #4444cc;
        border-radius: 8px; padding: 12px 16px;
        color: #8888ff; font-family: monospace; font-size: 14px;
    }
    @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.7; } }

    /* Log table */
    .log-entry {
        font-family: monospace; font-size: 12px;
        border-bottom: 1px solid #1a2540;
        padding: 4px 0; color: #8aaac8;
    }
    .log-safe { color: #4daa6a; }
    .log-warn { color: #cc9900; }
    .log-danger { color: #ff4444; }
    .log-rollback { color: #6666ff; }

    /* Spike animation */
    .spike-flash {
        background: #ff1111; color: white;
        font-size: 1.5rem; font-weight: bold;
        text-align: center; padding: 16px;
        border-radius: 8px;
        animation: flashbg 0.5s ease-in-out;
    }
    @keyframes flashbg { 0% { background:#ff0000; } 100% { background:#330000; } }

    /* Buttons */
    .stButton > button {
        background: #0d1e3a; border: 1px solid #2a5080;
        color: #4dd8ff; border-radius: 6px;
    }
    .stButton > button:hover { background: #1a3560; border-color: #4dd8ff; }

    /* Toggle */
    .stToggle { color: #e0e6f0; }

    /* Divider */
    hr { border-color: #1e2a40; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "brain" not in st.session_state:
    st.session_state.brain = NeuromorphicBrain()
if "watcher" not in st.session_state:
    st.session_state.watcher = NeuralWatch(st.session_state.brain)
if "running" not in st.session_state:
    st.session_state.running = False
if "tick" not in st.session_state:
    st.session_state.tick = 0
if "drift_history" not in st.session_state:
    st.session_state.drift_history = []
if "membrane_history" not in st.session_state:
    st.session_state.membrane_history = []
if "attack_mode" not in st.session_state:
    st.session_state.attack_mode = False
if "tampered" not in st.session_state:
    st.session_state.tampered = False
if "last_status" not in st.session_state:
    st.session_state.last_status = "SAFE"


# ─────────────────────────────────────────────
# LAYER 1 — GESTURE LOCK SCREEN
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 40px; background:#0d1220;
                    border: 1px solid #1e3a5f; border-radius: 12px;'>
            <div style='font-size:4rem;'>🧠</div>
            <h1 style='color:#4dd8ff; font-size:2rem; margin:16px 0 8px;'>NeuralWatch</h1>
            <p style='color:#4a6a8a; font-size:1rem; margin-bottom:24px;'>
                Neuromorphic AI Integrity Monitor<br>
                <span style='font-size:0.85rem;'>Layer 1 — Biometric Authentication Required</span>
            </p>
            <hr style='border-color:#1e3a5f; margin: 20px 0;'>
            <p style='color:#7a9bbf; font-size:0.9rem;'>
                To unlock: perform the authorized hand gesture<br>
                in front of your webcam, or use demo bypass below.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🖐 Launch Gesture Auth", use_container_width=True):
                # Import here to avoid crashing if not installed
                try:
                    from gesture_lock import run_gesture_authentication
                    with st.spinner("Opening webcam... show 2 fingers to unlock"):
                        result = run_gesture_authentication()
                    if result:
                        st.session_state.authenticated = True
                        st.success("Gesture recognized — access granted!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Authentication failed or cancelled.")
                except Exception as e:
                    st.error(f"Camera error: {e}")

        with col_b:
            if st.button("⚡ Demo Bypass (no webcam)", use_container_width=True):
                st.session_state.authenticated = True
                st.rerun()

        st.markdown("""
        <p style='text-align:center; color:#2a4060; font-size:11px; margin-top:24px;'>
            Unauthorized access attempts are logged and cryptographically signed.
        </p>
        """, unsafe_allow_html=True)

    st.stop()   # Don't render anything below until authenticated


# ─────────────────────────────────────────────
# MAIN DASHBOARD (authenticated users only)
# ─────────────────────────────────────────────

brain = st.session_state.brain
watcher = st.session_state.watcher

# ── HEADER ──────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
    <span style='font-size:2rem;'>🧠</span>
    <div>
        <h1 style='margin:0; font-size:1.8rem; color:#4dd8ff;'>NeuralWatch</h1>
        <p style='margin:0; color:#4a6a8a; font-size:0.85rem;'>
            Neuromorphic AI Integrity Monitor — All systems online
        </p>
    </div>
    <div style='margin-left:auto; background:#0a1a0a; border:1px solid #1a4a1a;
                border-radius:6px; padding:6px 14px; color:#4dff91; font-size:0.85rem;'>
        ● AUTHENTICATED
    </div>
</div>
<hr>
""", unsafe_allow_html=True)


# ── SIDEBAR CONTROLS ────────────────────────
with st.sidebar:
    st.markdown("### Control Panel")
    st.markdown("---")

    # Attack toggle — the drama button
    attack_mode = st.toggle(
        "💀 Simulate Attacker",
        value=st.session_state.attack_mode,
        help="Activates slow neural poisoning attack on the AI brain"
    )
    st.session_state.attack_mode = attack_mode

    if attack_mode:
        st.markdown("""
        <div style='background:#200a0a; border:1px solid #4a0000;
                    border-radius:6px; padding:10px; font-size:12px; color:#ff6666;'>
            ⚠ Attacker active — slowly poisoning neural weights
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#0a1a0a; border:1px solid #0a4a0a;
                    border-radius:6px; padding:10px; font-size:12px; color:#4daa6a;'>
            ✓ No active attack detected
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶ Start", use_container_width=True):
            st.session_state.running = True
    with col_stop:
        if st.button("⏸ Pause", use_container_width=True):
            st.session_state.running = False

    if st.button("🔄 Rollback Brain", use_container_width=True):
        watcher.perform_rollback()
        st.session_state.drift_history = []
        st.session_state.membrane_history = []
        st.session_state.tick = 0
        st.session_state.attack_mode = False
        st.session_state.last_status = "SAFE"
        st.success("Brain rolled back to clean state!")

    st.markdown("---")
    st.markdown("### Layer 3 — Audit Integrity")

    if st.button("🔍 Verify Log Chain", use_container_width=True):
        integrity = watcher.verify_log_integrity()
        if integrity:
            st.success("✅ Log integrity: VERIFIED")
        else:
            st.error("🚨 TAMPER DETECTED — Log chain broken!")

    if st.button("🔓 Simulate Tamper Attack", use_container_width=True):
        if watcher.audit_log:
            watcher.simulate_tamper()
            st.session_state.tampered = True
            st.warning("Log entry corrupted! Now click Verify.")
        else:
            st.info("Start monitoring first to generate logs.")

    st.markdown("---")
    if st.button("🚪 Lock Dashboard", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.running = False
        st.rerun()

    st.markdown(f"""
    <div style='font-size:11px; color:#2a4060; margin-top:16px;'>
        Session started: {watcher.monitoring_start}<br>
        Log entries: {len(watcher.audit_log)}<br>
        Rollbacks performed: {watcher.rollback_count}
    </div>
    """, unsafe_allow_html=True)


# ── METRIC CARDS ────────────────────────────
drift_now = brain.get_drift_score()
membrane_now = round(brain.membrane_potential, 4)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        "Neural Drift Score",
        f"{drift_now:.4f}",
        delta=f"threshold: 0.12",
        delta_color="off"
    )
with m2:
    st.metric(
        "Membrane Potential",
        f"{membrane_now:.4f}",
        delta=f"spike at: 0.15",
        delta_color="off"
    )
with m3:
    st.metric("Total Spikes Fired", watcher.total_spikes)
with m4:
    st.metric("Rollbacks Performed", watcher.rollback_count)

st.markdown("<br>", unsafe_allow_html=True)


# ── LIVE STATUS ALERT ───────────────────────
status_box = st.empty()
spike_flash = st.empty()

st.markdown("<br>", unsafe_allow_html=True)


# ── CHARTS ──────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("#### Neural Drift Over Time")
    st.caption("Safe zone: below 0.12 | Warning: 0.12–0.15 | Spike fires: above 0.15")
    drift_chart = st.empty()

with col_right:
    st.markdown("#### LIF Membrane Potential")
    st.caption("Neuromorphic spike model — resets to 0 after firing")
    membrane_chart = st.empty()

st.markdown("---")


# ── AUDIT LOG ───────────────────────────────
st.markdown("#### Live Audit Log — Cryptographically Signed")
log_display = st.empty()


# ─────────────────────────────────────────────
# MAIN MONITORING LOOP
# ─────────────────────────────────────────────
def render_status(status, drift, spike_fired):
    if spike_fired:
        return f"""<div class='alert-danger'>
            🚨 NEUROMORPHIC SPIKE DETECTED &nbsp;|&nbsp;
            Drift: {drift:.5f} &nbsp;|&nbsp;
            LIF threshold crossed — CONFIRMED POISONING ATTACK<br>
            <small>Rollback recommended immediately</small>
        </div>"""
    elif status == "WARNING":
        return f"""<div class='alert-warning'>
            ⚠ WARNING — Drift approaching threshold &nbsp;|&nbsp;
            Drift: {drift:.5f} &nbsp;|&nbsp;
            Monitoring for spike pattern
        </div>"""
    elif status == "ROLLBACK":
        return """<div class='alert-rollback'>
            🔄 ROLLBACK COMPLETE — Brain restored to verified baseline
        </div>"""
    else:
        return f"""<div class='alert-safe'>
            ✓ SAFE — Normal neuromorphic learning &nbsp;|&nbsp;
            Drift: {drift:.5f} &nbsp;|&nbsp; No anomalies detected
        </div>"""


def render_log(audit_log):
    if not audit_log:
        return "<p style='color:#2a4060; font-size:12px;'>No log entries yet. Start monitoring.</p>"

    rows = ""
    for e in reversed(audit_log[-20:]):  # show last 20
        color_class = {
            "SAFE": "log-safe",
            "WARNING": "log-warn",
            "SPIKE": "log-danger",
            "ROLLBACK": "log-rollback"
        }.get(e.get("status", "SAFE"), "log-safe")

        attack_flag = "⚡ATK" if e.get("attack_mode") else "   "
        spike_flag = "★SPIKE" if e.get("spike") else "      "

        rows += f"""
        <div class='log-entry {color_class}'>
            [{e.get('time','--:--:--')}] {e.get('tick','---')}&nbsp;&nbsp;
            STATUS:{e.get('status','---'):8}&nbsp;
            DRIFT:{e.get('drift',0):.5f}&nbsp;
            MEM:{e.get('membrane',0):.4f}&nbsp;
            {attack_flag}&nbsp;{spike_flag}&nbsp;&nbsp;
            SIG:{e.get('signature','--------')}
        </div>"""
    return rows


# Render initial state
drift_vals = st.session_state.drift_history or [0.0]
mem_vals = st.session_state.membrane_history or [0.0]

drift_df = pd.DataFrame({"Drift Score": drift_vals})
mem_df = pd.DataFrame({"Membrane Potential": mem_vals})

drift_chart.line_chart(drift_df, color="#4dd8ff", height=220)
membrane_chart.line_chart(mem_df, color="#ff6644", height=220)
status_box.markdown(render_status("SAFE", 0, False), unsafe_allow_html=True)
log_display.markdown(render_log(watcher.audit_log), unsafe_allow_html=True)


# Live update loop
if st.session_state.running:
    for _ in range(200):   # run for up to 200 ticks (~100 seconds)
        if not st.session_state.running:
            break

        tick = st.session_state.tick
        attack = st.session_state.attack_mode

        # Update brain
        if attack:
            brain.receive_poison(intensity=0.007)
        else:
            brain.learn_normally()

        # Monitor tick
        result = watcher.monitor_tick(tick, attack)
        st.session_state.tick += 1

        # Update histories
        st.session_state.drift_history.append(result["drift"])
        st.session_state.membrane_history.append(result["membrane"])

        # Keep chart history manageable
        if len(st.session_state.drift_history) > 80:
            st.session_state.drift_history = st.session_state.drift_history[-80:]
            st.session_state.membrane_history = st.session_state.membrane_history[-80:]

        # Re-render charts
        drift_df = pd.DataFrame({"Drift Score": st.session_state.drift_history})
        mem_df = pd.DataFrame({"Membrane Potential": st.session_state.membrane_history})

        # Add threshold reference line
        drift_df["Safe Limit"] = 0.12
        drift_df["Spike Threshold"] = 0.15

        drift_chart.line_chart(drift_df, color=["#4dd8ff", "#334422", "#442222"], height=220)
        membrane_chart.line_chart(mem_df, color="#ff6644", height=220)

        # Update status
        status_box.markdown(
            render_status(result["status"], result["drift"], result["spike_fired"]),
            unsafe_allow_html=True
        )

        # Spike flash effect
        if result["spike_fired"]:
            spike_flash.markdown(
                "<div class='spike-flash'>⚡ NEUROMORPHIC SPIKE FIRED ⚡</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.8)
            spike_flash.empty()

        # Update log
        log_display.markdown(render_log(watcher.audit_log), unsafe_allow_html=True)

        st.session_state.last_status = result["status"]

        time.sleep(0.5)   # half-second ticks for dramatic effect

    st.session_state.running = False
    st.rerun()
