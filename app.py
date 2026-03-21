# app.py

import streamlit as st
from main import evaluate, feedback

st.set_page_config(page_title="CogniTrust v4.0", layout="centered")

st.title("🧠 CogniTrust v4.0")
st.write("Multi-Source AI Confidence Evaluation")

statement = st.text_input("Enter a statement:")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("Evaluate"):
    if statement.strip():
        result = evaluate(statement)
        st.session_state.last_result = result

if st.session_state.last_result:
    result = st.session_state.last_result

    st.subheader("Result")
    st.write(f"**Score:** {result['score']:.3f}" if result["score"] else "No score")
    st.write(f"**Confidence Level:** {result['level']} {result['symbol']}")
    st.write(f"**Explanation:** {result['explanation']}")

    st.subheader("Backend Breakdown")
    for b in result["backend_results"]:
        st.write(f"{b['name']}: {b['score']}")

    st.subheader("Feedback")
    col1, col2 = st.columns(2)

    if col1.button("👍 Correct"):
        feedback(result, True)
        st.success("Feedback recorded")

    if col2.button("👎 Incorrect"):
        feedback(result, False)
        st.warning("Feedback recorded")