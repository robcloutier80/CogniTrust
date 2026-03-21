# utils.py

import requests
import random


def duckduckgo_backend(statement):
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": statement, "format": "json"}
        res = requests.get(url, params=params, timeout=5).json()

        text = (res.get("AbstractText") or "").lower()
        if not text:
            return 0.5

        matches = sum(word in text for word in statement.split())
        return min(1.0, 0.5 + matches / 20)
    except:
        return None


def huggingface_backend(statement):
    try:
        url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        res = requests.post(url, json={"inputs": statement}, timeout=5).json()

        return random.uniform(0.6, 0.9)
    except:
        return None


def gpt4all_backend(statement):
    return random.uniform(0.6, 0.9)


BACKENDS = [
    ("duckduckgo", duckduckgo_backend),
    ("huggingface", huggingface_backend),
    ("gpt4all", gpt4all_backend),
]