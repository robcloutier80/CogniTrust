# explain.py

def generate_explanation(statement, backend_results, score):
    if score is None:
        return "Unable to determine confidence due to lack of backend data."

    valid = [b for b in backend_results if b["score"] is not None]

    if not valid:
        return "All backends failed to produce a result."

    avg = sum(b["score"] for b in valid) / len(valid)

    if avg > 0.85:
        tone = "strong agreement across sources"
    elif avg > 0.7:
        tone = "moderate agreement across sources"
    else:
        tone = "mixed or weak agreement across sources"

    return f"The system evaluated multiple sources and found {tone}, resulting in a confidence score of {score:.2f}."