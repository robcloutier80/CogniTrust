# main.py - Cognitrust v5.0
from utils import BACKENDS, gpt4all_backend, huggingface_backend
from learner import load_learning, get_weight, update_weights
from calibration import calibrate_score
from explain import generate_explanation

learning_data = load_learning()


def weighted_aggregate(backend_results):
    total = 0
    weight_sum = 0
    used = 0

    for b in backend_results:
        if b["score"] is None:
            continue

        w = get_weight(b["name"], learning_data)
        total += b["score"] * w
        weight_sum += w
        used += 1

    if weight_sum == 0:
        return None, True  # no valid scores, treat as partial

    return total / weight_sum, used < len(backend_results)


def get_level(score):
    if score is None:
        return "red", "🛑"

    # Four-tier system, contextual thresholds
    if score >= 0.95:
        return "green", "✅"
    elif score >= 0.85:
        return "yellow", "⚠️"
    elif score >= 0.65:
        return "orange", "❗"
    else:
        return "red", "🛑"


def evaluate(statement):
    backend_results = []

    for name, func in BACKENDS:
        try:
            score = func(statement)
        except Exception as e:
            score = None

        backend_results.append({"name": name, "score": score})

    raw_score, partial = weighted_aggregate(backend_results)
    calibrated = calibrate_score(raw_score)

    level, symbol = get_level(calibrated)
    explanation = generate_explanation(statement, backend_results, calibrated)

    return {
        "score": calibrated,
        "raw_score": raw_score,
        "partial": partial,
        "level": level,
        "symbol": symbol,
        "backend_results": backend_results,
        "explanation": explanation
    }


def feedback(result, correct=True):
    update_weights(result["backend_results"], correct, learning_data)