"""
explain.py - CogniTrust v5.0
Generates human-readable explanations of evaluation results.
"""

from __future__ import annotations
from typing import Optional


def generate_explanation(
    statement: str,
    backend_results: list[dict],
    final_score: Optional[float],
    partial: bool,
) -> str:
    """
    Produce a plain-English summary of the evaluation.

    Covers:
    - Overall confidence signal
    - Degree of agreement across backends
    - Whether any backends failed (partial result)
    - A note on the reliability of the assessment
    """
    valid = [b for b in backend_results if b.get("score") is not None]
    failed = [b for b in backend_results if b.get("score") is None]
    total = len(backend_results)

    # ── No data at all ─────────────────────────────────────────────────────────
    if final_score is None or not valid:
        if failed:
            names = ", ".join(b["name"] for b in failed)
            return (
                f"All {total} backend(s) failed to return data ({names}). "
                "No confidence estimate could be formed. "
                "Check your network connection or API credentials."
            )
        return "No backends are configured. Confidence cannot be assessed."

    # ── Compute variance for agreement language ────────────────────────────────
    scores = [b["score"] for b in valid]
    avg = sum(scores) / len(scores)
    variance = sum((s - avg) ** 2 for s in scores) / len(scores)

    if variance < 0.01:
        agreement = "strong agreement"
    elif variance < 0.04:
        agreement = "moderate agreement"
    else:
        agreement = "notable disagreement"

    # ── Confidence narrative ───────────────────────────────────────────────────
    if final_score >= 0.90:
        confidence_narrative = "high confidence"
    elif final_score >= 0.75:
        confidence_narrative = "moderate confidence"
    elif final_score >= 0.55:
        confidence_narrative = "low confidence"
    else:
        confidence_narrative = "insufficient confidence to reach a reliable verdict"

    # ── Source count ──────────────────────────────────────────────────────────
    source_str = f"{len(valid)} of {total} source(s)"
    partial_note = (
        f" ({len(failed)} source(s) unavailable: "
        + ", ".join(b["name"] for b in failed)
        + ")"
        if partial
        else ""
    )

    # ── Assemble ──────────────────────────────────────────────────────────────
    explanation = (
        f"{source_str} returned signals{partial_note}, "
        f"showing {agreement}. "
        f"The aggregated assessment is {confidence_narrative} "
        f"(score: {final_score:.2f})."
    )

    if partial:
        explanation += " Results should be interpreted with caution given incomplete source coverage."

    return explanation
