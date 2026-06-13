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
"""

import time
import pandas as pd
import streamlit as st

from neural_brain import NeuromorphicBrain
from neuralwatch import NeuralWatch
from gesture_lock import run_gesture_authentication_ui

st.set_page_config(
    page_title="NeuralWatch",
    page_icon="🧠",
    layout="wide",
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


# ---------------------------------------------------------------------------
# Layer 1 - Gesture lock gate
# ---------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🧠 NeuralWatch")
    st.caption("Neuromorphic AI Integrity Monitor for Cybersecurity")
    st.divider()

    if run_gesture_authentication_ui(st):
        st.session_state.authenticated = True
        st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# Main dashboard (post-authentication)
# ---------------------------------------------------------------------------
st.title("🧠 NeuralWatch — Live Monitor")

brain = st.session_state.brain
watch = st.session_state.watch

# --- Sidebar controls -------------------------------------------------------
with st.sidebar:
    st.header("Controls")

    if not st.session_state.monitoring:
        if st.button("▶ Start Monitoring", type="primary", use_container_width=True):
            st.session_state.monitoring = True
            st.rerun()
    else:
        if st.button("⏸ Pause Monitoring", use_container_width=True):
            st.session_state.monitoring = False
            st.rerun()

    st.session_state.attack_mode = st.toggle(
        "⚠️ Simulate Attacker (poison weights)",
        value=st.session_state.attack_mode,
    )

    st.divider()

    if st.button("⏮ Rollback Brain", use_container_width=True):
        watch.perform_rollback()
        st.success("Brain rolled back to clean baseline.")

    if st.button("🧪 Simulate Tamper Attack", use_container_width=True):
        watch.simulate_tamper()
        st.warning("Last log entry tampered with (drift hidden).")

    if st.button("🔍 Verify Log Chain", use_container_width=True):
        if watch.verify_log_integrity():
            st.success("✅ Audit chain intact — no tampering detected.")
        else:
            st.error("🚨 CHAIN BROKEN — tampering detected!")

    st.divider()
    st.metric("Total Spikes", watch.total_spikes)
    st.metric("Rollbacks", watch.rollback_count)


# --- Top metrics -------------------------------------------------------------
drift = brain.get_drift_score()
membrane = round(brain.membrane_potential, 4)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Tick", st.session_state.tick)
m2.metric("Drift Score", f"{drift:.5f}")
m3.metric("Membrane Potential", f"{membrane:.4f}", help=f"Spike threshold: {brain.threshold}")
m4.metric("Status", "🟢 SAFE" if not watch.alert_active else "🔴 ALERT")

if watch.alert_active:
    st.error("🚨 SPIKE FIRED — possible AI poisoning detected. Consider rollback.")

st.divider()

# --- Drift / membrane chart ---------------------------------------------------
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.line_chart(df.set_index("tick")[["drift", "membrane"]])
else:
    st.info("Click **Start Monitoring** in the sidebar to begin.")

st.divider()

# --- Audit log ---------------------------------------------------------------
st.subheader("📜 Cryptographic Audit Log")
if watch.audit_log:
    log_df = pd.DataFrame(watch.audit_log)
    st.dataframe(log_df, use_container_width=True, hide_index=True)
else:
    st.caption("No log entries yet.")


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
    })

    time.sleep(1)
    st.rerun()
