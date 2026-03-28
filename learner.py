"""
learner.py - CogniTrust v5.0
Persistent merit-based weighting for backends. Every backend starts equal.
Correct predictions increase seniority; wrong ones reduce voting power.
Uses a floor so no backend ever loses its voice entirely.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from config import logger, AGENT_RECORDS_FILE, AGENT_WEIGHT_FLOOR, AGENT_CONFIDENCE_GATE

# Thread safety for concurrent Streamlit callbacks
_lock = threading.Lock()


# ── Persistence ────────────────────────────────────────────────────────────────

def load_records() -> dict[str, Any]:
    """Load agent performance records from disk. Returns empty dict if absent."""
    if not AGENT_RECORDS_FILE.exists():
        return {}
    try:
        with open(AGENT_RECORDS_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.error("agent_records.json is malformed — resetting.")
            return {}
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load agent records: %s", exc)
        return {}


def _save_records(data: dict[str, Any]) -> None:
    """Persist agent records to disk atomically (write-then-rename)."""
    tmp_path = AGENT_RECORDS_FILE.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(AGENT_RECORDS_FILE)
    except OSError as exc:
        logger.error("Failed to save agent records: %s", exc)
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


# ── Weight Calculation ─────────────────────────────────────────────────────────

def get_weight(agent_name: str, records: dict[str, Any]) -> float:
    """
    Compute the current trust weight for an agent.
    Formula: (successes + 1) / (total + 2)  — Laplace smoothing, starts at 0.5
    Floor: AGENT_WEIGHT_FLOOR (default 0.1) so agents can never be silenced.
    """
    record = records.get(agent_name, {"success": 0, "failure": 0})
    successes = int(record.get("success", 0))
    failures  = int(record.get("failure",  0))
    total = successes + failures

    if total == 0:
        return 1.0  # New agent: full baseline weight

    # Laplace-smoothed success rate
    weight = (successes + 1) / (total + 2)
    return max(AGENT_WEIGHT_FLOOR, weight)


# ── Feedback Processing ────────────────────────────────────────────────────────

def update_weights(
    backend_results: list[dict[str, Any]],
    user_approved: bool,
) -> None:
    """
    Update agent weights based on user feedback.

    Logic:
    - A backend "voted confident" if its score >= AGENT_CONFIDENCE_GATE.
    - If the user approved AND the backend was confident → success (+1).
    - If the user rejected AND the backend was confident → failure (+1).
    - Backends that abstained (score=None) or were non-committal are not penalized.

    Reads fresh from disk on each call — safe for concurrent Streamlit sessions.
    """
    with _lock:
        records = load_records()

        for b in backend_results:
            name  = b.get("name")
            score = b.get("score")

            if name is None or score is None:
                continue  # backend failed — no vote, no penalty

            if name not in records:
                records[name] = {"success": 0, "failure": 0}

            backend_was_confident = score >= AGENT_CONFIDENCE_GATE

            if backend_was_confident:
                if user_approved:
                    records[name]["success"] += 1
                    logger.info("Learner: %s → success (score=%.3f)", name, score)
                else:
                    records[name]["failure"] += 1
                    logger.info("Learner: %s → failure (score=%.3f)", name, score)

        _save_records(records)


# ── Summary ────────────────────────────────────────────────────────────────────

def get_weight_summary() -> list[dict[str, Any]]:
    """Return a sorted list of agent records with their current weights."""
    records = load_records()
    summary = []
    for name, rec in records.items():
        successes = rec.get("success", 0)
        failures  = rec.get("failure",  0)
        summary.append({
            "name":     name,
            "success":  successes,
            "failure":  failures,
            "total":    successes + failures,
            "weight":   get_weight(name, records),
        })
    return sorted(summary, key=lambda x: x["weight"], reverse=True)
