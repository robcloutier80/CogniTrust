# calibration.py

def calibrate_score(score):
    if score is None:
        return None

    # Simple calibration curve (can be replaced later)
    if score > 0.9:
        return min(1.0, score + 0.05)
    elif score < 0.5:
        return max(0.0, score - 0.05)

    return score