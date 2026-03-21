# learner.py

import json
import os

FILE = "learning.json"


def load_learning():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return {"weights": {}}


def save_learning(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_weight(name, data):
    return data["weights"].get(name, 1.0)


def update_weights(results, correct, data):
    for b in results:
        if b["score"] is None:
            continue

        name = b["name"]
        w = data["weights"].get(name, 1.0)

        delta = 0.03 * b["score"]
        w = w + delta if correct else w - delta

        data["weights"][name] = max(0.2, min(2.5, w))

    save_learning(data)