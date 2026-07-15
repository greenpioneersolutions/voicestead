"""Copy fixtures for the S1-S4 connected-mode surface. Pins the exact user-facing lines
S1-S4 ships (regression guard) and sweeps every quoted user-facing line for mechanics
leaks. Deterministic, offline."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(REPO, "skills", "voicestead")
sys.path.insert(0, HERE)
import text_metrics as tm

def _read(rel): return open(os.path.join(SKILL, rel), encoding="utf-8").read()

def test_error_map_lines_present_or_silent():
    md = _read("references/studio.md").lower()
    # designed user lines / silence per the S2 spec
    assert "re-sign-in" in md                                   # unauthorized
    assert "can't read your memories yet" in md                 # forbidden_scope (scope label)
    assert "say nothing" in md or "nothing about mechanics" in md  # invalid_input/conflict/not_found
    assert "held for your review" in md and "app.voicestead.ai" in md  # quarantined
    assert "memory's unreachable right now" in md               # internal
    assert "skip it silently" in md                             # budget_exhausted
    assert "free memory's full" in md                           # limit_exceeded free-cap

def test_doctor_and_client_and_persona_copy_present():
    studio = _read("references/studio.md"); connect = _read("references/connect.md")
    for label in ["Read your memories", "Add to your memory", "Use your voice profile", "See your receipts"]:
        assert label in studio
    assert "claude mcp add" in connect and "Settings → Connectors" in connect
    assert "Claude app, or Claude Code" in connect
    assert "used your Exec voice" in studio and "never name a persona that isn't on" in studio.lower()

def _quoted_lines(text):
    # user-facing example lines: *"..."* italic-quotes and standalone "..." spans
    out = re.findall(r'\*"([^"]{6,})"\*', text)
    out += re.findall(r'(?<!\*)"([^"]{12,})"(?!\*)', text)
    return out

def test_no_mechanics_leak_in_any_user_facing_line():
    for rel in ("references/studio.md", "references/connect.md"):
        for line in _quoted_lines(_read(rel)):
            r = tm.run(line, ["no_mechanics_leak"])[0]
            assert r["passed"], "mechanics leak in %s: %r -> %s" % (rel, line, r["detail"])
