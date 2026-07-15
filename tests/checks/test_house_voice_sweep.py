"""The voice we sell must pass its own bar. Sweeps every user-facing quoted line added
in S1-S4 (studio.md, connect.md) and the README's prose with the tells battery.
Targets the quoted lines (not whole procedural files, which would false-positive on
rhythm). Deterministic, offline."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import text_metrics as tm

TELLS = ["no_high_conf_tells", "tell_flags", "formula_structures", "zombie_nouns", "false_agency"]

def _read(p): return open(p, encoding="utf-8").read()
def _quoted(text):
    # Spoken example lines wrap in *"..."* and hard-wrap across source lines; capture them
    # NON-GREEDY (stops at the first "*, never spans into prose) plus single-line bare quotes.
    # (Same wrap-safe extraction as tests/checks/test_studio_copy.py::_quoted_lines.)
    italic = re.findall(r'\*"(.+?)"\*', text, re.S)
    bare = re.findall(r'(?<!\*)"([^"\n]{6,})"(?!\*)', text)
    return [re.sub(r"\s+", " ", s).strip() for s in italic + bare]

def _strip_readme(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))  # drop the Before slop

def test_user_facing_lines_pass_the_tells_bar():
    lines = []
    for rel in ("skills/voicestead/references/studio.md", "skills/voicestead/references/connect.md"):
        lines += _quoted(_read(os.path.join(REPO, rel)))
    for line in lines:
        bad = [r for r in tm.run(line, TELLS) if not r["passed"]]
        assert not bad, "house-voice line trips its own bar: %r -> %s" % (line, [b["detail"] for b in bad])

def test_readme_prose_passes_the_tells_bar():
    bad = [r for r in tm.run(_strip_readme(_read(os.path.join(REPO, "README.md"))), TELLS) if not r["passed"]]
    assert not bad, "README prose trips the tells bar: %s" % [b["detail"] for b in bad]
