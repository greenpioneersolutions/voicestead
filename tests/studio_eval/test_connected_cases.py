import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TESTS = os.path.dirname(HERE)
sys.path.insert(0, TESTS)
import run_skill

def test_connected_cases_wellformed_and_seam_renders():
    cases = json.load(open(os.path.join(HERE, "connected_cases.json")))
    seen = set()
    for c in cases:
        assert c["id"] not in seen; seen.add(c["id"])
        assert c.get("prompt")
        assert c.get("connection") is None or isinstance(c["connection"], dict)
        assert any(k in c for k in ("must_contain_any","must_contain_all","must_not_contain","count","count_max"))
        run_skill.build_system(load=c.get("load", []), connection=c.get("connection"))  # renders, no raise
