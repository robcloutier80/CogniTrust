import requests
import gpt4all
import os

# Initialize GPT4All model globally to avoid reloading on every click
# Replace 'orca-mini-3b-v0.3.q4_0.gguf' with your preferred local model file
try:
    model = gpt4all.GPT4All("orca-mini-3b-v0.3.q4_0.gguf")
except Exception as e:
    print(f"GPT4All Load Warning: {e}")
    model = None

def duckduckgo_backend(statement):
    """Checks statement against DuckDuckGo Abstract API for factual overlap."""
    try:
        url = "https://api.duckduckgo.com"
        params = {"q": statement, "format": "json"}
        res = requests.get(url, params=params, timeout=5).json()

        text = (res.get("AbstractText") or "").lower()
        if not text:
            return 0.5 # Neutral if no search result found

        # Count how many words from the statement appear in the search result
        words = [w for w in statement.lower().split() if len(w) > 3]
        if not words: return 0.5
        
        matches = sum(1 for word in words if word in text)
        score = 0.5 + (matches / len(words)) * 0.5
        return min(1.0, score)
    except:
        return None

def huggingface_backend(statement):
    """Uses a Zero-Shot Classification model to check 'entailment' vs 'contradiction'."""
    # This requires an API Key in your .env file as HUGGINGFACE_TOKEN
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        return None # Gracefully fail if no token

    try:
        api_url = "https://api-inference.huggingface.co"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": statement,
            "parameters": {"candidate_labels": ["true", "false", "uncertain"]}
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=5).json()
        
        # Extract the score for the 'true' label
        if "labels" in response:
            idx = response["labels"].index("true")
            return response["scores"][idx]
        return 0.5
    except:
        return None

def gpt4all_backend(statement):
    """Uses the local GPT4All model to self-evaluate the confidence of the statement."""
    if model is None:
        return None

    try:
        # Prompting the model to act as a judge
        prompt = f"Rate the factual confidence of this statement from 0.0 to 1.0. Reply ONLY with the number: '{statement}'"
        with model.chat_session():
            response = model.generate(prompt, max_tokens=10).strip()
        
        # Try to extract a float from the response
        import re
        match = re.search(r"[-+]?\d*\.\d+|\d+", response)
        if match:
            score = float(match.group())
            return max(0.0, min(1.0, score))
        return 0.7 # Default if it blathered instead of giving a number
    except:
        return None

BACKENDS = [
    ("duckduckgo", duckduckgo_backend),
    ("huggingface", huggingface_backend),
    ("gpt4all", gpt4all_backend),
]
