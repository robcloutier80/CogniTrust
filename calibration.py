def calibrate_score(score):
    if score is None:
        return 0.5
    
    # Push high scores higher and low scores lower
    if score > 0.8:
        return min(1.0, score + 0.05)
    elif score < 0.4:
        return max(0.0, score - 0.05)
        
    return score
