# main.py

"""
CogniTrust v2.2 – Functional Confidence Scoring Module
Author: Rob Cloutier
License: MIT
Purpose: Provides confidence scores (green/yellow/orange/red) for statements using open-source APIs.
"""

from utils import fetch_fact, compute_confidence

# Confidence thresholds
CONFIDENCE_LEVELS = {
    "green": 0.98,
    "yellow": 0.80,
    "orange": 0.60,
    "red": 0.0
}

class CogniTrust:
    def __init__(self):
        self.sources = []

    def check_statement(self, statement):
        """
        Check a statement and return:
        - confidence (0.0-1.0)
        - level (red/orange/yellow/green)
        - sources used
        """
        fetched_info = fetch_fact(statement)
        confidence = compute_confidence(statement, fetched_info)

        # Determine color level
        if confidence >= CONFIDENCE_LEVELS["green"]:
            level = "green"
        elif confidence >= CONFIDENCE_LEVELS["yellow"]:
            level = "yellow"
        elif confidence >= CONFIDENCE_LEVELS["orange"]:
            level = "orange"
        else:
            level = "red"

        self.sources = fetched_info.get("sources", [])

        return {
            "statement": statement,
            "confidence": round(confidence, 2),
            "level": level,
            "sources": self.sources
        }

if __name__ == "__main__":
    ct = CogniTrust()
    test_statements = [
        "The earth orbits the sun.",
        "Electric cars cannot recharge while driving."
    ]

    for s in test_statements:
        result = ct.check_statement(s)
        print(f"Statement: {result['statement']}")
        print(f"Confidence: {result['confidence']} ({result['level']})")
        if result['sources']:
            print(f"Sources: {', '.join(result['sources'])}")
        print("-" * 40)