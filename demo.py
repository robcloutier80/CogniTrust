# demo.py
"""
Interactive demo for CogniTrust v2.1
"""

from main import main

print("CogniTrust v2.1 Demo — Confidence-Weighted AI Responses")
print("Enter 'exit' to quit.")

while True:
    user_input = input("\nYour Query: ")
    if user_input.lower() == "exit":
        break
    main()