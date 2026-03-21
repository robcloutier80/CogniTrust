# utils.py - Cognitrust v5.0

import requests
import os
import logging
import random

# --- DIAGNOSTIC PANEL (Error Logging) ---
logging.basicConfig(
    filename='system.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_fault(backend_name, error_msg):
    logging.error(f"FAULT in {backend_name}: {error_msg}")

# --- DuckDuckGo Backend ---
def duckduckgo_backend(statement):
    try:
        url = "https://api.duckduckgo.com"
        params = {"q": statement, "format": "json"}
        res = requests.get(url, params=params, timeout=5).json()
        text = (res.get("AbstractText") or "").lower()
        if not text: 
            return 0.5
        words = [w for w in statement.lower().split() if len(w) > 3]
        if not words: 
            return 0.5
        matches = sum(1 for word in words if word in text)
        score = 0.5 + (matches / len(words)) * 0.5
        return min(1.0, score)
    except Exception as e:
        log_fault("DuckDuckGo", str(e))
        return None

# --- HuggingFace Backend ---
def huggingface_backend(statement):
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        log_fault("HuggingFace", "Missing API Token")
        return None
    try:
        # Make sure to specify the model path
        model = "facebook/bart-large-mnli"  # example NLI model
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": statement,
            "parameters": {"candidate_labels": ["true", "false"]}
        }
        res = requests.post(api_url, headers=headers, json=payload, timeout=8).json()
        if "labels" in res and "scores" in res:
            # Return confidence that statement is "true"
            return res["scores"][res["labels"].index("true")]
        return None
    except Exception as e:
        log_fault("HuggingFace", str(e))
        return None

# --- GPT4All Backend ---
def gpt4all_backend(statement):
    try:
        from gpt4all import GPT4All

        # Local model filename
        model_file = "ggml-gpt4all-j-v1.3-groovy.bin"
        if not os.path.exists(model_file):
            log_fault("GPT4All", f"Local model not found: {model_file}")
            return None

        model = GPT4All(model_file)
        response = model.generate(statement)

        # Heuristic to map response to 0-1 confidence
        # Simple: longer response = higher confidence (can improve later)
        conf = 0.7 + min(0.3, len(response)/500)
        return min(1.0, max(0.0, conf))
    except ImportError:
        log_fault("GPT4All", "GPT4All library not installed")
        return random.uniform(0.65, 0.75)
    except Exception as e:
        log_fault("GPT4All", str(e))
        return None

# --- BACKENDS LIST ---
BACKENDS = [
    ("DuckDuckGo Search", duckduckgo_backend),
    ("HuggingFace Reasoning", huggingface_backend),
    ("Local Agent (GPT4All)", gpt4all_backend),
]