# demo.py - CogniTrust v4.0 CLI demo
import sys
from utils import evaluate_statement, load_cache, save_cache

CACHE_FILE = "cache.json"

def print_banner():
    print("="*50)
    print("CogniTrust v4.0 - Multi-Backend Confidence Evaluator")
    print("Estimates confidence for statements using multiple backends")
    print("Type 'quit' to exit")
    print("="*50)

def print_result(statement, result):
    symbol = result.get("symbol", "?")
    level = result.get("level", "unknown")
    message = result.get("message", "")
    partial = result.get("partial", False)
    contextual = result.get("contextual", False)
    backend_scores = result.get("backend_scores", [])
    from_cache = result.get("from_cache", False)

    print("\n--- Evaluation Result ---")
    print(f"Statement: {statement}")
    cached_str = " (cached)" if from_cache else ""
    print(f"Result: {symbol} [{level}] - {message}{cached_str}")
    mode_str = "contextual thresholds" if contextual else "empirical thresholds"
    completeness_str = "partial" if partial else "complete"
    print(f"Mode: {mode_str}, backend data: {completeness_str}")
    print("Per-backend scores:")
    for backend in backend_scores:
        name = backend.get("name", "unknown")
        score = backend.get("score")
        score_str = f"{score:.3f}" if isinstance(score, (int, float)) else "FAILED or unavailable"
        print(f"  {name}: {score_str}")
    print("-"*50 + "\n")

def main():
    cache = load_cache(CACHE_FILE)

    print_banner()
    try:
        while True:
            statement = input("Enter statement to evaluate: ").strip()
            if statement.lower() in ["quit", "exit"]:
                print("Exiting demo. Goodbye!")
                break
            if not statement:
                print("Please enter a non-empty statement.\n")
                continue

            result = evaluate_statement(statement, cache=cache)
            print_result(statement, result)

            # Save cache after each evaluation
            save_cache(cache, CACHE_FILE)

    except EOFError:
        print("\nEOF received. Exiting demo.")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Goodbye!")
    finally:
        save_cache(cache, CACHE_FILE)

if __name__ == "__main__":
    main()