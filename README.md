🧠 CogniTrust v4.0

Multi-Source AI Confidence Evaluation System with Adaptive Learning
📋 CogniTrust v5.0 — "The Meritocratic Update"
Release Date: 2026-03-21
Status: Production-Ready (GCP & Local)
🚀 What’s New in v5.0?
1. Persistent Merit-Based Voting (The "Seniority" System)
The system no longer treats all AI backends equally. It now tracks the Historical Success and Failure of every agent in a local agent_records.json vault.
The Reward: Agents that consistently provide correct diagnostics gain "Seniority" (higher weight).
The Penalty: Hallucinating agents have their "Voting Power" automatically throttled.
2. Human-in-the-Loop Training (Feedback Loop)
Version 5.0 introduces Active Reinforcement. Every time a user confirms or denies a diagnostic via the Streamlit UI, the system re-calculates the internal reliability weights of every active backend.
3. "Smart Grid" Fault Tolerance
The backend architecture has been hardened with a Diagnostic Panel (Error Logging). If an agent "trips a breaker" (API timeout or local model crash), the system:
Logs the fault in system.log.
Automatically re-routes the "Voter Logic" to the remaining healthy agents.
Prevents a single-point failure from crashing the entire UI.
4. Lightweight Cloud-Native "Airlock"
Optimized for Google Cloud Run. By isolating heavy local-inference libraries (like Torch/Transformers), the v5.0 container is 90% lighter, ensuring faster deployments and lower compute costs while maintaining "Reasoning" capabilities via the Hugging Face Inference API.
5. Enhanced Visualization
Voter Confidence Meter: A real-time progress bar reflecting the aggregated, weighted certainty of the collective.
Circuit Diagnostics Expanders: Deep-dive into the individual "voltages" (scores) of each backend to see exactly who is voting "Yes" or "No."
🛠 Technical Specs (V5.0)
Core Logic: Weighted Bayesian-style aggregation.
Persistence Layer: Local JSON vault for agent history.
Observability: Industrial-grade logging module integration.
Licensing: MIT (Open for Partnership and Commercial Integration).
---

🚀 Overview

CogniTrust is a modular system designed to evaluate the confidence of a statement using multiple independent AI and data sources.

Instead of relying on a single model, CogniTrust:

- Aggregates results from multiple backends
- Learns which sources are more reliable over time
- Adapts its weighting dynamically based on feedback
- Produces calibrated confidence scores with explanations

This transforms static AI evaluation into a living, learning system.

---

⚡ Key Features

🔗 Multi-Backend Evaluation

- DuckDuckGo (live search signal)
- HuggingFace inference (zero-shot classification ready)
- Local model placeholder (GPT4All-style)

---

🧠 Adaptive Learning Engine

- Persistent learning via "learning.json"
- Backend weights adjust based on feedback
- Reinforces reliable sources over time
- Penalizes inaccurate contributors

---

⚖️ Weighted Aggregation

- Not all sources are treated equally
- Scores are combined using dynamic weights
- Automatically adapts to real-world performance

---

📊 Calibration Layer

- Adjusts raw scores toward more realistic confidence values
- Prevents overconfidence and underconfidence drift

---

🧾 Explanation Engine

- Generates human-readable reasoning
- Summarizes agreement/disagreement across sources

---

🌐 One-Click Web UI

- Built with Streamlit
- Interactive evaluation + feedback loop
- No frontend development required

---

🖥️ Demo (Local)

1. Clone the repository

git clone <your-repo-url>
cd cognitrust

2. Install dependencies

pip install -r requirements.txt

3. Launch the app

streamlit run app.py

---

🧪 How It Works

1. User inputs a statement
2. Each backend evaluates it independently
3. Scores are weighted using learned trust levels
4. Result is calibrated for realism
5. System generates explanation
6. User provides feedback (correct / incorrect)
7. System updates backend weights

---

🔁 Feedback Loop

CogniTrust improves over time through user input:

- 👍 Correct → strengthens contributing backends
- 👎 Incorrect → reduces trust in those backends

All learning is persisted locally in:

learning.json

---

🧱 Project Structure

app.py              # Streamlit web interface
main.py             # Core orchestration logic
utils.py            # Backend integrations
learner.py          # Adaptive learning system
calibration.py      # Score calibration layer
explain.py          # Explanation generation
requirements.txt    # Dependencies
learning.json       # Persistent learning store (auto-created)

---

🔌 Backend Notes

DuckDuckGo

- Free, no API key required
- Provides lightweight real-time signal

HuggingFace

- Uses free inference API (optional)
- Can be upgraded with API key for stability

Local Models

- Placeholder included (GPT4All-style)
- Can be replaced with real local inference

---

⚠️ Limitations

- Free APIs may rate-limit or fail intermittently
- Some backends are placeholders by default
- Not a truth engine — this is a confidence estimation system

---

🛣️ Roadmap

v4.x

- Improved backend integrations
- Better calibration models
- Enhanced explanation synthesis

v5.0 (Planned)

- True ML-based confidence calibration
- Semantic clustering across sources
- Distributed backend orchestration
- Cloud deployment + public demo

---

🤝 Contributing

This project is intentionally open to:

- Backend additions
- Calibration improvements
- Better scoring logic
- UI enhancements

If you can break it — even better.
If you can improve it — even better.

---

💬 Feedback

Try it. Stress it. Break it.

- Where does it fail?
- Where is it overconfident?
- Which sources should be added?

Open an issue or submit a pull request.

---

📜 License

MIT License

---

🔥 Final Note

CogniTrust is not trying to answer:

«“Is this true?”»

It’s trying to answer:

«“How confident should we be — and why?”»

That distinction is everything.
📋 CogniTrust v5.0 — "The Meritocratic Update"
Release Date: 2026-03-21
Status: Production-Ready (GCP & Local)
🚀 What’s New in v5.0?
1. Persistent Merit-Based Voting (The "Seniority" System)
The system no longer treats all AI backends equally. It now tracks the Historical Success and Failure of every agent in a local agent_records.json vault.
The Reward: Agents that consistently provide correct diagnostics gain "Seniority" (higher weight).
The Penalty: Hallucinating agents have their "Voting Power" automatically throttled.
2. Human-in-the-Loop Training (Feedback Loop)
Version 5.0 introduces Active Reinforcement. Every time a user confirms or denies a diagnostic via the Streamlit UI, the system re-calculates the internal reliability weights of every active backend.
3. "Smart Grid" Fault Tolerance
The backend architecture has been hardened with a Diagnostic Panel (Error Logging). If an agent "trips a breaker" (API timeout or local model crash), the system:
Logs the fault in system.log.
Automatically re-routes the "Voter Logic" to the remaining healthy agents.
Prevents a single-point failure from crashing the entire UI.
4. Lightweight Cloud-Native "Airlock"
Optimized for Google Cloud Run. By isolating heavy local-inference libraries (like Torch/Transformers), the v5.0 container is 90% lighter, ensuring faster deployments and lower compute costs while maintaining "Reasoning" capabilities via the Hugging Face Inference API.
5. Enhanced Visualization
Voter Confidence Meter: A real-time progress bar reflecting the aggregated, weighted certainty of the collective.
Circuit Diagnostics Expanders: Deep-dive into the individual "voltages" (scores) of each backend to see exactly who is voting "Yes" or "No."
🛠 Technical Specs (V5.0)
Core Logic: Weighted Bayesian-style aggregation.
Persistence Layer: Local JSON vault for agent history.
Observability: Industrial-grade logging module integration.
Licensing: MIT (Open for Partnership and Commercial Integration).