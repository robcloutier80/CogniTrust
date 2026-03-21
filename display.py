# cognitrust/display.py
"""
Display module for CogniTrust v2.1
"""

def display_response(result, confidence, color, source_link):
    print(f"\nResponse: {result}")
    print(f"Confidence: {confidence*100:.1f}% [{color.upper()}]")
    print(f"Source: {source_link}")