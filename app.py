"""
app.py - CogniTrust v5.0
Streamlit web interface. Launch with: streamlit run app.py
"""

import streamlit as st
from engine import evaluate, submit_feedback
from learner import get_weight_summary

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CogniTrust v5.0",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ─────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🧠 CogniTrust v5.0")
st.caption("Multi-Source Confidence Evaluator — Adaptive Merit Weighting")
st.markdown("---")

# ── Input ──────────────────────────────────────────────────────────────────────
statement = st.text_input(
    "Enter a statement to evaluate:",
    placeholder="e.g. 'The Great Wall of China is visible from space.'",
    key="statement_input",
)

run_col, _ = st.columns([1, 4])
with run_col:
    run_clicked = st.button("▶ Evaluate", type="primary", use_container_width=True)

if run_clicked:
    if not statement.strip():
        st.warning("Please enter a statement before running.")
    else:
        with st.spinner("Querying backends…"):
            try:
                result = evaluate(statement)
                st.session_state.result = result
                st.session_state.feedback_submitted = False
            except Exception as exc:
                st.error(f"Evaluation error: {exc}")
                st.session_state.result = None

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.result:
    res = st.session_state.result

    st.markdown("---")

    # Tier banner
    tier_color = {
        "green": "#1a9e50",
        "yellow": "#c9a227",
        "orange": "#d4601a",
        "red": "#c0392b",
    }.get(res["tier"], "#888")

    st.markdown(
        f"<h2 style='color:{tier_color}'>{res['symbol']} {res['label']}</h2>",
        unsafe_allow_html=True,
    )
    st.caption(res["message"])

    # Score meter
    score = res["score"] if res["score"] is not None else 0.0
    st.progress(score, text=f"Confidence Score: {score:.2%}")

    # Explanation
    st.info(res["explanation"])

    # Partial warning
    if res["partial"]:
        st.warning("⚡ One or more backends were unavailable. Results reflect partial coverage.")

    # Per-backend detail
    with st.expander("🔬 Per-Backend Diagnostics"):
        for b in res["backend_results"]:
            score_str = f"{b['score']:.3f}" if b["score"] is not None else "— unavailable"
            icon = "✅" if b["score"] is not None and b["score"] >= 0.70 else (
                   "⚠️" if b["score"] is not None else "🛑"
            )
            st.text(f"{icon}  {b['name']:<30}  {score_str}")

    # ── Feedback ───────────────────────────────────────────────────────────────
    if not st.session_state.feedback_submitted:
        st.markdown("---")
        st.write("**Was this assessment correct?**")
        fb_col1, fb_col2, _ = st.columns([1, 1, 3])

        with fb_col1:
            if st.button("👍 Yes", key="fb_yes", use_container_width=True):
                submit_feedback(st.session_state.result, user_approved=True)
                st.session_state.feedback_submitted = True
                st.rerun()

        with fb_col2:
            if st.button("👎 No", key="fb_no", use_container_width=True):
                submit_feedback(st.session_state.result, user_approved=False)
                st.session_state.feedback_submitted = True
                st.rerun()
    else:
        st.success("✅ Feedback recorded. Backend weights updated.")

# ── Sidebar — Agent Seniority Panel ───────────────────────────────────────────
with st.sidebar:
    st.header("🏅 Agent Seniority")
    st.caption("Backend trust weights (merit-based)")
    summary = get_weight_summary()
    if summary:
        for agent in summary:
            bar_pct = agent["weight"]
            st.markdown(f"**{agent['name']}**")
            st.progress(bar_pct, text=f"Weight: {bar_pct:.2f}  |  ✅ {agent['success']}  ❌ {agent['failure']}")
    else:
        st.caption("No feedback recorded yet. All agents start equal.")

    st.markdown("---")
    st.caption("CogniTrust v5.0 — MIT License")
