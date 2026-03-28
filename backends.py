"""
backends.py - CogniTrust v5.0
All external signal sources live here. Each backend returns a float [0.0, 1.0]
on success, or None on failure. Never raises — callers expect clean None on error.
"""

from __future__ import annotations

import os
import requests
from typing import Optional

from config import (
    logger,
    REQUEST_TIMEOUT_SEARCH,
    REQUEST_TIMEOUT_INFERENCE,
    HUGGINGFACE_MODEL,
    HUGGINGFACE_TOKEN_ENV_KEY,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clamp(value: float) -> float:
    """Clamp a float to [0.0, 1.0]."""
    return max(0.0, min(1.0, value))


# ── DuckDuckGo Instant Answer Backend ─────────────────────────────────────────

def duckduckgo_backend(statement: str) -> Optional[float]:
    """
    Uses DuckDuckGo's Instant Answer API as a lightweight real-time signal.
    Confidence is derived from keyword overlap between the statement and the
    AbstractText returned. Returns 0.5 (neutral) when no abstract is found —
    absence of evidence is not evidence of absence.
    """
    try:
        url = "https://api.duckduckgo.com"
        params = {"q": statement, "format": "json", "no_html": "1", "skip_disambig": "1"}
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SEARCH)
        resp.raise_for_status()
        data = resp.json()

        abstract = (data.get("AbstractText") or "").lower()

        if not abstract:
            # No abstract — neutral signal, not a failure
            return 0.5

        # Keyword overlap scoring: only words longer than 3 chars are signal words
        keywords = [w for w in statement.lower().split() if len(w) > 3]
        if not keywords:
            return 0.5

        hits = sum(1 for kw in keywords if kw in abstract)
        # Base of 0.45 + up to 0.55 from keyword density
        score = 0.45 + (hits / len(keywords)) * 0.55
        return _clamp(score)

    except requests.exceptions.Timeout:
        logger.error("DuckDuckGo backend timed out for statement: %.60s", statement)
    except requests.exceptions.RequestException as exc:
        logger.error("DuckDuckGo backend request failed: %s", exc)
    except (ValueError, KeyError) as exc:
        logger.error("DuckDuckGo backend parse error: %s", exc)
    except Exception as exc:
        logger.error("DuckDuckGo backend unexpected error: %s", exc)

    return None


# ── HuggingFace Zero-Shot Classification Backend ──────────────────────────────

def huggingface_backend(statement: str) -> Optional[float]:
    """
    Uses HuggingFace's hosted Inference API with a zero-shot NLI model
    (facebook/bart-large-mnli) to classify the statement as 'true' vs 'false'.
    Requires HUGGINGFACE_TOKEN env var. Returns None gracefully if absent.
    """
    token = os.getenv(HUGGINGFACE_TOKEN_ENV_KEY)
    if not token:
        logger.warning(
            "HuggingFace backend skipped: %s env var not set.",
            HUGGINGFACE_TOKEN_ENV_KEY,
        )
        return None

    try:
        api_url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": statement,
            "parameters": {"candidate_labels": ["true", "false"]},
        }
        resp = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_INFERENCE,
        )
        resp.raise_for_status()
        data = resp.json()

        labels: list = data.get("labels", [])
        scores: list = data.get("scores", [])

        if not labels or not scores or "true" not in labels:
            logger.error("HuggingFace backend: unexpected response structure: %s", data)
            return None

        true_idx = labels.index("true")
        return _clamp(float(scores[true_idx]))

    except requests.exceptions.Timeout:
        logger.error("HuggingFace backend timed out.")
    except requests.exceptions.HTTPError as exc:
        logger.error("HuggingFace backend HTTP error: %s", exc)
    except requests.exceptions.RequestException as exc:
        logger.error("HuggingFace backend request failed: %s", exc)
    except (ValueError, KeyError, IndexError) as exc:
        logger.error("HuggingFace backend parse error: %s", exc)

    return None


# ── Wikipedia Summary Backend ──────────────────────────────────────────────────

def wikipedia_backend(statement: str) -> Optional[float]:
    """
    Queries Wikipedia's REST summary API using the first meaningful noun phrase
    from the statement. Confidence is derived from keyword overlap with the
    returned summary excerpt. Free, no API key required.
    """
    try:
        # Use the first 3+ char word as a search anchor
        words = [w.strip(".,!?\"'") for w in statement.split() if len(w.strip(".,!?\"'")) > 3]
        if not words:
            return 0.5

        # Try up to the first 3 words as individual lookups, take first hit
        for word in words[:3]:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{word}"
            resp = requests.get(
                url,
                timeout=REQUEST_TIMEOUT_SEARCH,
                headers={"User-Agent": "CogniTrust/5.0 (confidence-evaluator)"},
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            extract = (data.get("extract") or "").lower()
            if not extract:
                continue

            # Score by how many statement keywords appear in the extract
            keywords = [w for w in statement.lower().split() if len(w) > 3]
            if not keywords:
                return 0.5

            hits = sum(1 for kw in keywords if kw in extract)
            score = 0.40 + (hits / len(keywords)) * 0.60
            return _clamp(score)

        return 0.5  # No useful article found — neutral

    except requests.exceptions.Timeout:
        logger.error("Wikipedia backend timed out.")
    except requests.exceptions.RequestException as exc:
        logger.error("Wikipedia backend request failed: %s", exc)
    except (ValueError, KeyError) as exc:
        logger.error("Wikipedia backend parse error: %s", exc)
    except Exception as exc:
        logger.error("Wikipedia backend unexpected error: %s", exc)

    return None


# ── Backend Registry ───────────────────────────────────────────────────────────
# Each entry: (display_name, callable)
# Add new backends here — engine.py picks them up automatically.

BACKENDS: list[tuple[str, callable]] = [
    ("DuckDuckGo Search",       duckduckgo_backend),
    ("Wikipedia Summary",       wikipedia_backend),
    ("HuggingFace Reasoning",   huggingface_backend),
]
