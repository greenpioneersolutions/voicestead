#!/usr/bin/env python3
"""Structural guard: JSON validity, cases<->evals sync, manifests, frontmatter, fixture paths.

Runs in CI on every push. No key, no network. Catches the drift a corpus check can't:
a case added to cases.json but not mirrored to evals.json, a broken manifest, an over-long
description, or an eval whose loaded fixture went missing.

  python tests/checks/validate_repo.py
"""
import json
import os
import sys

try:
    import yaml
except ImportError:
    # pyyaml is a hard requirement: silently skipping the frontmatter check would let a
    # broken SKILL.md pass CI with zero signal. Fail loudly with an install hint instead.
    print("REPO VALIDATION FAILED:\n  - pyyaml is not installed (required for the frontmatter check).\n"
          "    install it: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import text_metrics as tm  # noqa: E402  (needs the sys.path insert above)

REPO = os.path.dirname(os.path.dirname(HERE))
# Rubric dimensions the judge scores (tests/judge/rubric.md). A must_pass entry may name
# one of these (enforced at tier2) in addition to any registered deterministic check id.
RUBRIC_DIMS = {"voice", "clarity", "persuasion", "human_rhythm", "restraint", "truth"}
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def _load(rel):
    return json.load(open(os.path.join(REPO, rel)))


# 1. Manifests parse
for p in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]:
    try:
        _load(p)
    except Exception as e:
        errors.append(f"{p}: invalid JSON: {e}")

# 2. cases.json <-> evals.json in sync
cases = _load("tests/cases.json")["evals"]
evals = _load("skills/voicestead/evals/evals.json")["evals"]
cids = [c["id"] for c in cases]
eids = [e["id"] for e in evals]
check(cids == eids, f"case id order/set mismatch: cases.json={cids} evals.json={eids}")
cmap = {c["id"]: c for c in cases}
emap = {e["id"]: e for e in evals}
for i in set(cids) & set(eids):
    check(cmap[i]["prompt"] == emap[i]["prompt"], f"case {i}: prompt differs between cases.json and evals.json")
for e in evals:
    check(isinstance(e.get("assertions"), list) and e["assertions"], f"eval {e.get('id')}: missing/empty assertions[]")

# 3. Frontmatter + description length (pyyaml guaranteed present -- see import guard)
fm = yaml.safe_load(open(os.path.join(REPO, "skills/voicestead/SKILL.md")).read().split("---")[1])
check(fm.get("name") == "voicestead", "SKILL.md: name is not 'voicestead'")
d = fm.get("description", "")
check(0 < len(d) <= 1024, f"SKILL.md: description length {len(d)} (must be 1..1024)")

# 4. Every fixture a case loads actually exists
SKILL = os.path.join(REPO, "skills/voicestead")
EVALS_DIR = os.path.join(SKILL, "evals")
for c in cases:
    for rel in c.get("load", []):
        check(os.path.isfile(os.path.join(SKILL, rel)), f"case {c['id']}: load fixture missing: {rel}")


def _cid(chk):
    return chk if isinstance(chk, str) else chk.get("id")


# 5. Every deterministic_checks / must_pass id resolves. A typo in a gate would run zero
# checks and report green -- catch it here. must_pass may also name a rubric dimension.
for c in cases:
    for chk in c.get("deterministic_checks", []):
        cid = _cid(chk)
        check(cid in tm.REGISTRY, f"case {c['id']}: unknown deterministic check '{cid}'")
    for mid in c.get("must_pass", []):
        check(mid in tm.REGISTRY or mid in RUBRIC_DIMS,
              f"case {c['id']}: must_pass '{mid}' is neither a registered check nor a rubric dimension")

# 6. Every evals.json files[] entry exists relative to the skill evals dir, and every
# fixture a case loads is wired into that case's evals files[] (matched by basename) so the
# judge actually sees the loaded profile/influences context it is grading against.
for e in evals:
    for rel in e.get("files", []):
        check(os.path.isfile(os.path.join(EVALS_DIR, rel)),
              f"eval {e['id']}: files entry missing (relative to evals dir): {rel}")
for c in cases:
    # Only example-profile fixtures (examples/*.example.md, cases 17-19) are graded
    # material the judge must be handed. references/*.md are the skill's own always-loaded
    # knowledge, not judge context, so they are not wired into evals files[].
    fixtures = [rel for rel in c.get("load", []) if rel.startswith("examples/")]
    if not fixtures:
        continue
    e = emap.get(c["id"], {})
    file_bases = {os.path.basename(f) for f in e.get("files", [])}
    for rel in fixtures:
        base = os.path.basename(rel)
        check(base in file_bases,
              f"case {c['id']}: loaded fixture '{base}' not wired into evals.json files[] {sorted(file_bases)}")

if errors:
    print("REPO VALIDATION FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"repo validation clean: {len(cases)} cases in sync (cases.json == evals.json), manifests valid, frontmatter ok, fixtures present")
