"""
test_launch.py - CogniTrust v5.0
Production launch test suite. All tests run offline — backends are mocked.
Covers: config, calibration, explain, learner, engine, and integration.
Run with: python test_launch.py
"""

import json
import sys
import os
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

# ── Redirect to module directory ───────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

PASS = "✅"
FAIL = "❌"
results = []


def test(name: str):
    """Decorator to register and run a named test."""
    def decorator(fn):
        try:
            fn()
            results.append((name, True, None))
        except AssertionError as e:
            results.append((name, False, str(e) or "AssertionError"))
        except Exception as e:
            results.append((name, False, f"{type(e).__name__}: {e}"))
        return fn
    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

@test("config: thresholds are ordered correctly")
def _():
    from config import THRESHOLDS
    assert THRESHOLDS["green"] > THRESHOLDS["yellow"] > THRESHOLDS["orange"]

@test("config: all tiers have required metadata keys")
def _():
    from config import TIER_META
    required = {"symbol", "label", "message"}
    for tier, meta in TIER_META.items():
        missing = required - set(meta.keys())
        assert not missing, f"Tier '{tier}' missing keys: {missing}"

@test("config: logger is initialised without error")
def _():
    from config import logger
    assert logger is not None
    logger.info("test log message")  # should not raise


# ══════════════════════════════════════════════════════════════════════════════
# CALIBRATION
# ══════════════════════════════════════════════════════════════════════════════

@test("calibration: None input returns None")
def _():
    from calibration import calibrate_score
    assert calibrate_score(None) is None

@test("calibration: high score gets boosted")
def _():
    from calibration import calibrate_score
    raw = 0.85
    cal = calibrate_score(raw)
    assert cal > raw, f"Expected boost, got {cal} <= {raw}"

@test("calibration: low score gets dragged down")
def _():
    from calibration import calibrate_score
    raw = 0.30
    cal = calibrate_score(raw)
    assert cal < raw, f"Expected drag, got {cal} >= {raw}"

@test("calibration: mid-range score is unchanged")
def _():
    from calibration import calibrate_score
    raw = 0.60
    cal = calibrate_score(raw)
    assert cal == raw, f"Expected pass-through, got {cal}"

@test("calibration: result always in [0.0, 1.0]")
def _():
    from calibration import calibrate_score
    for val in [-0.5, 0.0, 0.5, 0.99, 1.0, 1.5]:
        result = calibrate_score(val)
        if result is not None:
            assert 0.0 <= result <= 1.0, f"Out of range: calibrate_score({val}) = {result}"


# ══════════════════════════════════════════════════════════════════════════════
# EXPLAIN
# ══════════════════════════════════════════════════════════════════════════════

@test("explain: returns string for valid inputs")
def _():
    from explain import generate_explanation
    backends = [
        {"name": "A", "score": 0.8},
        {"name": "B", "score": 0.6},
    ]
    result = generate_explanation("test statement", backends, 0.72, False)
    assert isinstance(result, str) and len(result) > 0

@test("explain: handles all backends failed")
def _():
    from explain import generate_explanation
    backends = [{"name": "A", "score": None}, {"name": "B", "score": None}]
    result = generate_explanation("test", backends, None, True)
    assert isinstance(result, str) and len(result) > 0

@test("explain: partial flag is mentioned in output")
def _():
    from explain import generate_explanation
    backends = [{"name": "A", "score": 0.7}, {"name": "B", "score": None}]
    result = generate_explanation("test", backends, 0.65, True)
    assert "unavailable" in result.lower() or "caution" in result.lower() or "partial" in result.lower()

@test("explain: score value appears in output")
def _():
    from explain import generate_explanation
    backends = [{"name": "A", "score": 0.85}]
    result = generate_explanation("test", backends, 0.85, False)
    assert "0.85" in result


# ══════════════════════════════════════════════════════════════════════════════
# LEARNER
# ══════════════════════════════════════════════════════════════════════════════

@test("learner: new agent weight is 1.0")
def _():
    from learner import get_weight
    weight = get_weight("NewAgent", {})
    assert weight == 1.0

@test("learner: weight floors at AGENT_WEIGHT_FLOOR")
def _():
    from learner import get_weight
    from config import AGENT_WEIGHT_FLOOR
    records = {"WorstAgent": {"success": 0, "failure": 999}}
    weight = get_weight("WorstAgent", records)
    assert weight >= AGENT_WEIGHT_FLOOR, f"Weight {weight} below floor {AGENT_WEIGHT_FLOOR}"

@test("learner: perfect agent has high weight")
def _():
    from learner import get_weight
    records = {"PerfectAgent": {"success": 100, "failure": 0}}
    weight = get_weight("PerfectAgent", records)
    assert weight > 0.95, f"Expected high weight, got {weight}"

@test("learner: load/save round-trip is correct")
def _():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch the file path
        import learner
        orig = learner.AGENT_RECORDS_FILE

        test_file = Path(tmpdir) / "records.json"
        import config
        config.AGENT_RECORDS_FILE = test_file
        learner.AGENT_RECORDS_FILE = test_file

        data = {"TestAgent": {"success": 3, "failure": 1}}
        learner._save_records(data)
        loaded = learner.load_records()
        assert loaded == data, f"Round-trip mismatch: {loaded}"

        # Restore
        config.AGENT_RECORDS_FILE = orig
        learner.AGENT_RECORDS_FILE = orig

@test("learner: update_weights handles None scores gracefully")
def _():
    with tempfile.TemporaryDirectory() as tmpdir:
        import learner, config
        orig = learner.AGENT_RECORDS_FILE
        config.AGENT_RECORDS_FILE = Path(tmpdir) / "records.json"
        learner.AGENT_RECORDS_FILE = config.AGENT_RECORDS_FILE

        backend_results = [
            {"name": "GoodBackend", "score": None},  # failed — should be ignored
        ]
        learner.update_weights(backend_results, True)
        records = learner.load_records()
        # No entry should have been created for a failed backend
        assert "GoodBackend" not in records

        config.AGENT_RECORDS_FILE = orig
        learner.AGENT_RECORDS_FILE = orig

@test("learner: update_weights increments success correctly")
def _():
    with tempfile.TemporaryDirectory() as tmpdir:
        import learner, config
        orig = learner.AGENT_RECORDS_FILE
        config.AGENT_RECORDS_FILE = Path(tmpdir) / "records.json"
        learner.AGENT_RECORDS_FILE = config.AGENT_RECORDS_FILE

        backend_results = [{"name": "Backend1", "score": 0.90}]
        learner.update_weights(backend_results, True)
        records = learner.load_records()
        assert records.get("Backend1", {}).get("success", 0) == 1

        config.AGENT_RECORDS_FILE = orig
        learner.AGENT_RECORDS_FILE = orig

@test("learner: concurrent updates don't corrupt records")
def _():
    with tempfile.TemporaryDirectory() as tmpdir:
        import learner, config
        orig = learner.AGENT_RECORDS_FILE
        config.AGENT_RECORDS_FILE = Path(tmpdir) / "records.json"
        learner.AGENT_RECORDS_FILE = config.AGENT_RECORDS_FILE

        backend_results = [{"name": "ConcurrentAgent", "score": 0.85}]
        threads = [
            threading.Thread(target=learner.update_weights, args=(backend_results, True))
            for _ in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        records = learner.load_records()
        successes = records.get("ConcurrentAgent", {}).get("success", 0)
        assert successes == 5, f"Expected 5 successes, got {successes}"

        config.AGENT_RECORDS_FILE = orig
        learner.AGENT_RECORDS_FILE = orig


# ══════════════════════════════════════════════════════════════════════════════
# BACKENDS (unit — no real network)
# ══════════════════════════════════════════════════════════════════════════════

@test("backends: duckduckgo returns None on network failure")
def _():
    from backends import duckduckgo_backend
    with patch("backends.requests.get", side_effect=Exception("network down")):
        result = duckduckgo_backend("water is wet")
    assert result is None

@test("backends: duckduckgo returns 0.5 when no abstract")
def _():
    from backends import duckduckgo_backend
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"AbstractText": ""}
    mock_resp.raise_for_status.return_value = None
    with patch("backends.requests.get", return_value=mock_resp):
        result = duckduckgo_backend("something obscure")
    assert result == 0.5

@test("backends: duckduckgo scores higher with matching keywords")
def _():
    from backends import duckduckgo_backend
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "AbstractText": "water is a liquid that covers most of planet earth"
    }
    mock_resp.raise_for_status.return_value = None
    with patch("backends.requests.get", return_value=mock_resp):
        result = duckduckgo_backend("water covers the earth")
    assert result is not None and result > 0.5

@test("backends: huggingface returns None when token missing")
def _():
    from backends import huggingface_backend
    with patch.dict(os.environ, {}, clear=True):
        # Ensure token env var absent
        os.environ.pop("HUGGINGFACE_TOKEN", None)
        result = huggingface_backend("test statement")
    assert result is None

@test("backends: huggingface parses valid response correctly")
def _():
    from backends import huggingface_backend
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"labels": ["true", "false"], "scores": [0.82, 0.18]}
    mock_resp.raise_for_status.return_value = None
    with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "fake-token"}):
        with patch("backends.requests.post", return_value=mock_resp):
            result = huggingface_backend("the sky is blue")
    assert result is not None
    assert abs(result - 0.82) < 0.001

@test("backends: wikipedia returns None on failure")
def _():
    from backends import wikipedia_backend
    with patch("backends.requests.get", side_effect=Exception("network down")):
        result = wikipedia_backend("something")
    assert result is None

@test("backends: all backend names are non-empty strings")
def _():
    from backends import BACKENDS
    for name, func in BACKENDS:
        assert isinstance(name, str) and name.strip(), f"Invalid backend name: {name!r}"
        assert callable(func), f"Backend {name!r} is not callable"


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE (integration — backends fully mocked)
# ══════════════════════════════════════════════════════════════════════════════

def _mock_backends(scores: list):
    """Helper: patch BACKENDS with fakes returning given scores."""
    from backends import BACKENDS as real_backends
    fakes = []
    for i, (name, _) in enumerate(real_backends):
        score = scores[i] if i < len(scores) else None
        fakes.append((name, lambda s, _score=score: _score))
    return fakes

@test("engine: evaluate returns expected keys")
def _():
    import engine
    from backends import BACKENDS
    fakes = _mock_backends([0.8, 0.7, 0.9])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("test statement")
    required_keys = {"score", "raw_score", "partial", "tier", "label", "symbol", "message", "explanation", "backend_results"}
    missing = required_keys - set(result.keys())
    assert not missing, f"Missing keys: {missing}"

@test("engine: all backends returning 1.0 → green tier")
def _():
    import engine
    fakes = _mock_backends([1.0, 1.0, 1.0])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("clearly true statement")
    assert result["tier"] == "green", f"Expected green, got {result['tier']} (score={result['score']})"

@test("engine: all backends returning 0.0 → red tier")
def _():
    import engine
    fakes = _mock_backends([0.0, 0.0, 0.0])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("clearly false statement")
    assert result["tier"] == "red", f"Expected red, got {result['tier']} (score={result['score']})"

@test("engine: all backends failing → partial=True, score=None, tier=red")
def _():
    import engine
    fakes = _mock_backends([None, None, None])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("unknown statement")
    assert result["partial"] is True
    assert result["score"] is None
    assert result["tier"] == "red"

@test("engine: one backend failing → partial=True")
def _():
    import engine
    fakes = _mock_backends([0.8, None, 0.7])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("partial test")
    assert result["partial"] is True

@test("engine: empty statement raises ValueError")
def _():
    import engine
    try:
        engine.evaluate("   ")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

@test("engine: submit_feedback calls update_weights with correct args")
def _():
    import engine
    dummy_result = {
        "backend_results": [{"name": "A", "score": 0.8}]
    }
    with patch("engine.update_weights") as mock_uw:
        engine.submit_feedback(dummy_result, True)
        mock_uw.assert_called_once_with([{"name": "A", "score": 0.8}], True)

@test("engine: score is clamped to [0.0, 1.0]")
def _():
    import engine
    fakes = _mock_backends([0.99, 0.99, 0.99])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("high confidence test")
    if result["score"] is not None:
        assert 0.0 <= result["score"] <= 1.0

@test("engine: backend_results list length matches BACKENDS length")
def _():
    import engine
    from backends import BACKENDS
    fakes = _mock_backends([0.6, 0.7, 0.8])
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value={}):
        result = engine.evaluate("count test")
    assert len(result["backend_results"]) == len(fakes)

@test("engine: weighted agent with higher seniority influences score more")
def _():
    import engine
    # Two backends: A is high-trust, B is low-trust
    # A says 1.0, B says 0.0 — high-trust A should dominate
    records = {
        "AgentA": {"success": 100, "failure": 0},
        "AgentB": {"success": 0,   "failure": 100},
    }
    fakes = [
        ("AgentA", lambda s: 1.0),
        ("AgentB", lambda s: 0.0),
    ]
    with patch.object(engine, "BACKENDS", fakes), \
         patch("engine.load_records", return_value=records):
        result = engine.evaluate("seniority test")
    assert result["score"] is not None
    assert result["score"] > 0.5, f"Expected high-trust agent to dominate, score={result['score']}"


# ══════════════════════════════════════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_report():
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print("\n" + "═" * 60)
    print("  CogniTrust v5.0 — Launch Test Report")
    print("═" * 60)

    for name, ok, err in results:
        icon = PASS if ok else FAIL
        print(f"  {icon}  {name}")
        if err:
            print(f"       → {err}")

    print("═" * 60)
    print(f"  {len(passed)} passed  |  {len(failed)} failed  |  {len(results)} total")
    print("═" * 60 + "\n")

    if failed:
        print("LAUNCH BLOCKED — fix failures above before deploying.\n")
        sys.exit(1)
    else:
        print("✅  ALL TESTS PASSED — CogniTrust v5.0 is production-ready.\n")


if __name__ == "__main__":
    print_report()
