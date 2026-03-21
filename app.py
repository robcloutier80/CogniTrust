import streamlit as st
from main import evaluate, submit_feedback

st.set_page_config(page_title="CogniTrust v4.0", layout="centered")

st.title("🧠 CogniTrust v4.0")
st.write("Master Architect's Trust Panel: Diagnostic AI Confidence")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

statement = st.text_input("Enter a statement to verify:")

if st.button("Run Diagnostic"):
    if statement.strip():
        with st.spinner("Probing Backends..."):
            result = evaluate(statement)
            st.session_state.last_result = result

if st.session_state.last_result:
    res = st.session_state.last_result
    
    st.markdown(f"### Result: {res['symbol']} {res['level']}")
    st.progress(res['score'])
    st.write(f"**Voter Confidence Score:** {res['score']:.2f}")

    with st.expander("View Circuit Diagnostics (Per-Backend)"):
        for b in res["backend_results"]:
            score_display = f"{b['score']:.2f}" if b['score'] else "TRIPPED (Error)"
            st.text(f"Agent: {b['name']} | Score: {score_display}")

    st.write("---")
    st.write("Was this diagnostic correct?")
    col1, col2 = st.columns(2)
    
    if col1.button("👍 Yes (Reward Success)"):
        submit_feedback(res, True)
        st.success("Success recorded. Agent weights updated.")
        
    if col2.button("👎 No (Record Failure)"):
        submit_feedback(res, False)
        st.error("Failure recorded. Re-calibrating agent weights.")
