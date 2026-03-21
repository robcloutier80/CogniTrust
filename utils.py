# utils.py

"""
CogniTrust Utility Functions
Handles open-source API requests and confidence scoring
"""

import requests

FACT_API = "https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1"

def fetch_fact(statement):
    """
    Fetch information from open-source APIs.
    Returns a dict with 'data' and 'sources' keys.
    """
    try:
        response = requests.get(FACT_API.format(query=statement))
        if response.status_code == 200:
            data = response.json()
            sources = []
            abstract = data.get("AbstractText", "")
            if abstract:
                sources.append("DuckDuckGo Abstract")
            return {"data": abstract, "sources": sources}
        else:
            return {"data": "", "sources": []}
    except Exception:
        return {"data": "", "sources": []}

def compute_confidence(statement, fetched_info):
    """
    Compute a confidence score (0.0-1.0) based on presence of information.
    Green: >0.98, Yellow: 0.80-0.98, Orange: 0.60-0.80, Red: <0.60
    """
    data = fetched_info.get("data", "")
    if not data:
        return 0.0
    words = statement.lower().split()
    matches = sum(1 for w in words if w in data.lower())
    return min(1.0, matches / max(len(words), 1))