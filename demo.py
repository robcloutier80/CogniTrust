# demo.py
from main import evaluate_statement

def main():
    print("CogniTrust v2.3 Interactive Demo")
    print("Enter 'quit' to exit.\n")

    while True:
        statement = input("Enter a statement to evaluate: ").strip()
        if statement.lower() == "quit":
            print("Exiting demo.")
            break
        symbol, level, message = evaluate_statement(statement)
        print(f"{symbol} [{level}] - {message}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted. Goodbye!")