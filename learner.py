import json
import os

LEARNING_FILE = "agent_records.json"

def load_learning():
    if os.path.exists(LEARNING_FILE):
        try:
            with open(LEARNING_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_weight(agent_name, data):
    record = data.get(agent_name, {"success": 0, "failure": 0})
    successes = record["success"]
    failures = record["failure"]
    total = successes + failures
    
    if total == 0:
        return 1.0 # New agent baseline
    
    # Reward success: The more they get right, the higher the weight.
    # We use a 0.1 floor so they never completely lose their vote.
    weight = (successes + 1) / (total + 1) 
    return max(0.1, weight)

def update_weights(backend_results, user_correct, data):
    for b in backend_results:
        name = b["name"]
        score = b["score"]
        if score is None: continue

        if name not in data:
            data[name] = {"success": 0, "failure": 0}

        # Logic: If the agent's score matches the user's feedback, reward them.
        agent_was_confident = score >= 0.75
        
        if user_correct and agent_was_confident:
            data[name]["success"] += 1
        elif not user_correct and agent_was_confident:
            data[name]["failure"] += 1
            
    with open(LEARNING_FILE, "w") as f:
        json.dump(data, f, indent=4)
