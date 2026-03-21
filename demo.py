# demo.py
"""
CogniTrust v2.2 Interactive Demo
Run this file to try CogniTrust live: type statements and see confidence scores.
"""

from main import CogniTrust

def run_interactive_demo():
    ct = CogniTrust()
    print("CogniTrust v2.2 Interactive Demo")
    print("Type a statement and see confidence levels (green/yellow/orange/red).")
    print("Type 'exit' to quit.\n")

    while True:
        stmt = input("Enter a statement: ").strip()
        if stmt.lower() == "exit":
            print("Exiting interactive demo.")
            break
        if not stmt:
            continue

        result = ct.check_statement(stmt)
        print(f"\nStatement: {result['statement']}")
        print(f"Confidence: {result['confidence']} ({result['level']})")
        if result['sources']:
            print(f"Sources: {', '.join(result['sources'])}")
        print("-" * 40)

if __name__ == "__main__":
    run_interactive_demo()