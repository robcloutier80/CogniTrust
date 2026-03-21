# demo_streamlit.py - CogniTrust v4.0 Streamlit Web Demo
import streamlit as st
from utils import evaluate_statement, load_cache, save_cache

CACHE_FILE = "cache.json"

# Load or initialize cache
cache = load_cache(CACHE_FILE)

st.set_page_config(page_title="CogniTrust v4.0", layout="wide")
st.title("CogniTrust v4.0 - Multi-Backend Confidence Evaluator")
st.markdown(
    """
    This demo evaluates the confidence of statements using multiple backends.
    Enter a statement below, and see confidence levels, symbols, and per-backend scores.
    """
)

statement_input = st.text_input("Enter statement to evaluate:")

def display_result(statement, result):
    symbol = result.get("symbol", "?")
    level = result.get("level", "unknown")
    message = result.get("message", "")
    partial = result.get("partial", False)
    contextual = result.get("contextual", False)
    backend_scores = result.get("backend_scores", [])
    from_cache = result.get("from_cache", False)

    cached_str = " (cached)" if from_cache else ""
    st.subheader(f"Result: {symbol} [{level}] - {message}{cached_str}")

    mode_str = "contextual thresholds" if contextual else "empirical thresholds"
    completeness_str = "partial" if partial else "complete"
    st.markdown(f"**Mode:** {mode_str}, **Backend data:** {completeness_str}")

    st.markdown("**Per-backend scores:**")
    for backend in backend_scores:
        name = backend.get("name", "unknown")
        score = backend.get("score")
        score_str = f"{score:.3f}" if isinstance(score, (int, float)) else "FAILED or unavailable"
        st.text(f"{name}: {score_str}")

# Evaluate statement when user presses Enter
if statement_input:
    result = evaluate_statement(statement_input, cache=cache)
    display_result(statement_input, result)
    # Persist cache after evaluation
    save_cache(cache, CACHE_FILE)

st.markdown("---")
st.markdown("Type another statement above or refresh to start a new session.")