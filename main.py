# main.py
"""
CogniTrust v2.1 — Confidence-Weighted AI Response System
Author: Rob Cloutier, 2026
"""

from cognitrust.confidence import ConfidenceEvaluator
from cognitrust.display import display_response

def main():
    evaluator = ConfidenceEvaluator()
    
    user_input = input("Enter your query: ")
    
    result, confidence, color, source_link = evaluator.evaluate(user_input)
    
    display_response(result, confidence, color, source_link)

if __name__ == "__main__":
    main()