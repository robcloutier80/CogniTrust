"""
calibration.py - CogniTrust v5.0
Adjusts raw aggregated scores toward more realistic confidence values.
Applies a soft S-curve: amplifies decisive signals, compresses the middle.
"""

from __future__ import annotations
from typing import Optional

from config import (
    CALIBRATION_HIGH_THRESHOLD,
    CALIBRATION_HIGH_BOOST,
    CALIBRATION_LOW_THRESHOLD,
    CALIBRATION_LOW_DRAG,
)


def calibrate_score(score: Optional[float]) -> Optional[float]:
    """
    Apply a calibration pass to a raw aggregated score.

    Rules:
    - None input → None output (caller decides how to render "no data")
    - High scores (> HIGH_THRESHOLD) get a small boost toward conviction
    - Low scores (< LOW_THRESHOLD) get a small drag toward caution
    - Middle band passes through unchanged

    Result is always clamped to [0.0, 1.0].
    """
    if score is None:
        return None

    if score > CALIBRATION_HIGH_THRESHOLD:
        calibrated = score + CALIBRATION_HIGH_BOOST
    elif score < CALIBRATION_LOW_THRESHOLD:
        calibrated = score - CALIBRATION_LOW_DRAG
    else:
        calibrated = score

    return max(0.0, min(1.0, calibrated))
