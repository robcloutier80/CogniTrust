# main.py
from utils import fetch_sources, load_cache, save_cache, is_contextual
import json

# Confidence thresholds
THRESHOLDS = {
    "empirical": {"green": 0.99, "yellow": 0.85, "orange": 0.65, "red": 0.0},
    "contextual": {"green": 0.95, "yellow": 0.75, "orange": 0.65, "red": 0.0},
}

SYMBOLS = {"green": "✅", "yellow": "⚠️", "orange": "❗", "red": "🛑"}

CACHE_FILE = "cache.json"
CACHE = load_cache(CACHE_FILE)

def get_confidence_level(score, contextual=False):
    levels = THRESHOLDS["contextual"] if contextual else THRESHOLDS["empirical"]
    for level in ["green", "yellow", "orange", "red"]:
        if score >= levels[level]:
            return level
    return "red"

def aggregate_confidences(confidences):
    if not confidences:
        return None, True  # None score, partial
    valid_scores = [c for c in confidences if c is not None]
    if not valid_scores:
        return None, True
    avg_score = sum(valid_scores) / len(valid_scores)
    partial = len(valid_scores) < len(confidences)
    return avg_score, partial

def evaluate_statement(statement):
    contextual = is_contextual(statement)
    backend_scores = []

    # Query all open-source backends
    for source_func in fetch_sources:
        try:
            score = source_func(statement)
            backend_scores.append(score)
        except Exception:
            backend_scores.append(None)

    final_score, partial = aggregate_confidences(backend_scores)
    if final_score is None:
        level = "red"
        symbol = SYMBOLS[level]
        message = "Unable to complete"
    else:
        level = get_confidence_level(final_score, contextual)
        symbol = SYMBOLS[level]
        message = f"{final_score*100:.1f}%"
        if partial:
            message += " (partial)"

    # Save cache
    save_cache(CACHE_FILE, CACHE)
    return symbol, level, message