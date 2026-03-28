"""
engine.py - CogniTrust v5.0
Core orchestration: runs all backends, aggregates, calibrates, explains.
This is the single entry point for all evaluation and feedback logic.
"""

from __future__ import annotations

from typing import Any, Optional

from backends import BACKENDS
from calibration import calibrate_score
from config import THRESHOLDS, TIER_META, logger
from explain import generate_explanation
from learner import get_weight, load_records, update_weights


# ── Tier Resolution ────────────────────────────────────────────────────────────

def _resolve_tier(score: Optional[float]) -> str:
    """Map a calibrated score to a tier name."""
    if score is None:
        return "red"
    if score >= THRESHOLDS["green"]:
        return "green"
    if score >= THRESHOLDS["yellow"]:
        return "yellow"
    if score >= THRESHOLDS["orange"]:
        return "orange"
    return "red"


# ── Weighted Aggregation ───────────────────────────────────────────────────────

def _weighted_aggregate(
    backend_results: list[dict[str, Any]],
    records: dict[str, Any],
) -> tuple[Optional[float], bool]:
    """
    Compute a weighted mean of backend scores.
    Returns (aggregated_score, is_partial).
    is_partial=True when one or more backends returned None.
    """
    total_weighted = 0.0
    weight_sum = 0.0
    valid_count = 0

    for b in backend_results:
        score = b.get("score")
        if score is None:
            continue
        w = get_weight(b["name"], records)
        total_weighted += score * w
        weight_sum += w
        valid_count += 1

    is_partial = valid_count < len(backend_results)

    if weight_sum == 0:
        return None, True

    return total_weighted / weight_sum, is_partial


# ── Public API ─────────────────────────────────────────────────────────────────

def evaluate(statement: str) -> dict[str, Any]:
    """
    Evaluate a statement against all registered backends.

    Returns a result dict with:
      score          float | None  – calibrated final score
      raw_score      float | None  – pre-calibration aggregate
      partial        bool          – True if ≥1 backend failed
      tier           str           – 'green' | 'yellow' | 'orange' | 'red'
      label          str           – human tier label
      symbol         str           – emoji symbol for the tier
      message        str           – short tier description
      explanation    str           – full plain-English explanation
      backend_results list[dict]   – per-backend {name, score}
    """
    statement = statement.strip()
    if not statement:
        raise ValueError("Statement must be a non-empty string.")

    logger.info("Evaluating: %.80s", statement)

    # ── Run all backends ───────────────────────────────────────────────────────
    backend_results: list[dict[str, Any]] = []
    for name, func in BACKENDS:
        try:
            score = func(statement)
        except Exception as exc:
            logger.error("Backend %r raised unexpectedly: %s", name, exc)
            score = None
        backend_results.append({"name": name, "score": score})

    # ── Aggregate ──────────────────────────────────────────────────────────────
    records = load_records()
    raw_score, is_partial = _weighted_aggregate(backend_results, records)
    calibrated = calibrate_score(raw_score)

    # ── Tier & metadata ────────────────────────────────────────────────────────
    tier = _resolve_tier(calibrated)
    meta = TIER_META[tier]

    # ── Explanation ────────────────────────────────────────────────────────────
    explanation = generate_explanation(statement, backend_results, calibrated, is_partial)

    logger.info(
        "Result for '%.60s': tier=%s score=%.3f partial=%s",
        statement,
        tier,
        calibrated if calibrated is not None else -1.0,
        is_partial,
    )

    return {
        "score":           calibrated,
        "raw_score":       raw_score,
        "partial":         is_partial,
        "tier":            tier,
        "label":           meta["label"],
        "symbol":          meta["symbol"],
        "message":         meta["message"],
        "explanation":     explanation,
        "backend_results": backend_results,
    }


def submit_feedback(result: dict[str, Any], user_approved: bool) -> None:
    """
    Record user feedback and update backend weights.

    Args:
        result:        The result dict returned by evaluate().
        user_approved: True if the user agreed with the assessment.
    """
    update_weights(result["backend_results"], user_approved)
    logger.info("Feedback recorded: approved=%s", user_approved)
