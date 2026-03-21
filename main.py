from utils import BACKENDS
from learner import load_learning, get_weight, update_weights
from calibration import calibrate_score

def evaluate(statement):
    learning_data = load_learning()
    backend_results = []
    
    # 1. Collect Raw Scores
    for name, func in BACKENDS:
        try:
            score = func(statement)
        except:
            score = None
        backend_results.append({"name": name, "score": score})

    # 2. Weighted Voter Logic
    weighted_sum = 0
    total_weight = 0
    for b in backend_results:
        if b["score"] is not None:
            w = get_weight(b["name"], learning_data)
            weighted_sum += b["score"] * w
            total_weight += w

    if total_weight == 0:
        raw_score = 0.5
    else:
        raw_score = weighted_sum / total_weight

    # 3. Calibration & Result Generation
    calibrated = calibrate_score(raw_score)
    
    if calibrated >= 0.85:
        level, symbol = "GREEN", "✅"
    elif calibrated >= 0.65:
        level, symbol = "YELLOW", "⚠️"
    else:
        level, symbol = "RED", "🛑"

    return {
        "score": calibrated,
        "level": level,
        "symbol": symbol,
        "backend_results": backend_results,
        "statement": statement
    }

def submit_feedback(result, user_says_correct):
    data = load_learning()
    update_weights(result["backend_results"], user_says_correct, data)
