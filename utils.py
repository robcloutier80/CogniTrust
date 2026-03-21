# utils.py
import json
import os
import requests
import random

CACHE = {}

# Example backend functions
def fetch_duckduckgo(statement):
    # Placeholder: return random score for demonstration
    return random.uniform(0.6, 1.0)

def fetch_haystack(statement):
    return random.uniform(0.65, 1.0)

def fetch_llama2(statement):
    return random.uniform(0.7, 1.0)

def fetch_mpt(statement):
    return random.uniform(0.65, 0.95)

def fetch_gpt4all(statement):
    return random.uniform(0.7, 0.99)

# Ordered list of backend functions for main.py
fetch_sources = [
    fetch_duckduckgo,
    fetch_haystack,
    fetch_llama2,
    fetch_mpt,
    fetch_gpt4all
]

def load_cache(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(file_path, cache_data):
    with open(file_path, "w") as f:
        json.dump(cache_data, f)

def is_contextual(statement):
    # Placeholder logic: treat short statements as empirical
    return len(statement.split()) > 10