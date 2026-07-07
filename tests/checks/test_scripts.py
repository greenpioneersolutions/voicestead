#!/usr/bin/env python3
"""Guard-the-guards: prove the tooling FAILS when it should.

Every check in this repo is only as trustworthy as its ability to go red. These tests
tamper with a temp copy of the tree and assert the relevant script exits non-zero — the
canary being a curly-apostrophe slop injection that a naive matcher would wave through.

  python -m pytest tests/checks/test_scripts.py -q

No API key, no network. Runs on Python 3.9 and 3.12.
"""
import json
import os
import shutil
import subprocess
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "*.skill", "results")


def _copy(dst, *items):
    """Copy selected top-level repo items (dirs or files) into dst; return dst."""
    os.makedirs(dst, exist_ok=True)
    for item in items:
        src = os.path.join(REPO, item)
        target = os.path.join(dst, item)
        if os.path.isdir(src):
            shutil.copytree(src, target, ignore=_IGNORE)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(src, target)
    return dst


def _run(script_relpath, *args, cwd=None, env=None):
    """Run a repo script (path relative to REPO or an absolute path) via subprocess."""
    script = script_relpath if os.path.isabs(script_relpath) else os.path.join(REPO, script_relpath)
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, script, *args],
        cwd=cwd or REPO, env=full_env, capture_output=True, text=True,
    )


# --------------------------------------------------------------------------- package_skill

def test_package_builds_and_excludes_personal(tmp_path):
    root = _copy(str(tmp_path / "repo"), "scripts", "skills")
    skill = os.path.join(root, "skills", "voicestead")
    # Plant personal-by-design files at the skill root.
    open(os.path.join(skill, "voice-profile.md"), "w").write("# my private voice\n")
    open(os.path.join(skill, "influences.md"), "w").write("# my private influences\n")
    out = str(tmp_path / "out.skill")

    r = _run(os.path.join(root, "scripts", "package_skill.py"), "voicestead", "--out", out)
    assert r.returncode == 0, r.stderr + r.stdout
    assert "excluding personal file" in r.stdout

    names = zipfile.ZipFile(out).namelist()
    assert "voicestead/SKILL.md" in names
    # The shippable template MUST survive.
    assert "voicestead/examples/voice-profile.example.md" in names
    # The planted personal files MUST NOT ship.
    leaked = [n for n in names if os.path.basename(n) in ("voice-profile.md", "influences.md")]
    assert leaked == [], "personal files leaked into archive: %s" % leaked


def test_package_corrupt_dir_exits1(tmp_path):
    root = _copy(str(tmp_path / "repo"), "scripts", "skills")
    os.remove(os.path.join(root, "skills", "voicestead", "SKILL.md"))
    r = _run(os.path.join(root, "scripts", "package_skill.py"), "voicestead",
             "--out", str(tmp_path / "out.skill"))
    assert r.returncode == 1, r.stdout + r.stderr


# --------------------------------------------------------------------------- validate_repo

def test_validate_real_repo_green():
    r = _run("tests/checks/validate_repo.py")
    assert r.returncode == 0, r.stdout + r.stderr


def _validate_copy(tmp_path):
    return _copy(str(tmp_path / "repo"), "scripts", "skills", "tests", ".claude-plugin")


def _run_copied_validate(root):
    return _run(os.path.join(root, "tests", "checks", "validate_repo.py"), cwd=root)


def test_validate_desynced_cases_evals_exits1(tmp_path):
    root = _validate_copy(tmp_path)
    ev = os.path.join(root, "skills", "voicestead", "evals", "evals.json")
    import json
    d = json.load(open(ev))
    d["evals"].pop()  # drop the last eval so cases.json and evals.json desync
    json.dump(d, open(ev, "w"), indent=2)
    r = _run_copied_validate(root)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "mismatch" in r.stdout


def test_validate_broken_frontmatter_exits1(tmp_path):
    root = _validate_copy(tmp_path)
    skill_md = os.path.join(root, "skills", "voicestead", "SKILL.md")
    text = open(skill_md).read().replace("name: voicestead", "name: TOTALLY-BROKEN")
    assert "TOTALLY-BROKEN" in text
    open(skill_md, "w").write(text)
    r = _run_copied_validate(root)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "name is not" in r.stdout


def test_validate_unknown_check_id_exits1(tmp_path):
    root = _validate_copy(tmp_path)
    cases = os.path.join(root, "tests", "cases.json")
    import json
    d = json.load(open(cases))
    d["evals"][0]["deterministic_checks"].append("no_invented_numers")  # typo'd gate
    json.dump(d, open(cases, "w"), indent=2)
    r = _run_copied_validate(root)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "unknown deterministic check" in r.stdout


def test_validate_pyyaml_missing_exits1(tmp_path):
    # Shim pyyaml out of existence; the frontmatter check must fail hard, never skip.
    shim = tmp_path / "shim"
    shim.mkdir()
    (shim / "yaml.py").write_text("raise ImportError('pyyaml shimmed out for the test')\n")
    r = _run("tests/checks/validate_repo.py", env={"PYTHONPATH": str(shim)})
    assert r.returncode != 0, r.stdout + r.stderr
    assert "pyyaml" in (r.stdout + r.stderr)


# --------------------------------------------------------------------------- corpus (run_checks)

def test_corpus_real_green():
    r = _run("tests/checks/run_checks.py", "--corpus", os.path.join(REPO, "tests", "corpus"),
             cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_corpus_curly_apostrophe_canary(tmp_path):
    # THE CANARY: the exact unicode variant ("today’s", curly apostrophe) that a
    # non-normalizing matcher lets slip. Injecting it must turn the corpus red.
    corpus = str(tmp_path / "corpus")
    shutil.copytree(os.path.join(REPO, "tests", "corpus"), corpus)
    good = os.path.join(corpus, "good-email.txt")
    slop = ("In today’s rapidly evolving landscape, it’s not just about the migration"
            "—it’s about connection. Let’s delve into it.\n\n")
    original = open(good, encoding="utf-8").read()
    open(good, "w", encoding="utf-8").write(slop + original)

    r = _run("tests/checks/run_checks.py", "--corpus", corpus,
             cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 1, "canary failed to fire:\n" + r.stdout + r.stderr


# --------------------------------------------------------------------------- single output (run_checks)

def test_single_output_default_checks_catch_fabrication(tmp_path):
    # Negative-path canary for the DEFAULT --checks wiring: with no --checks flag,
    # the truth gates must still run, so a fabricated URL and a fabricated quote
    # must exit 1. Guards the default list itself — corpus mode never exercises it
    # because manifests supply explicit check lists.
    out = tmp_path / "out.txt"
    out.write_text('Docs live at https://docs.example.com/setup if you get stuck. '
                   'She said "we will never miss a deadline again this year."\n')
    r = _run("tests/checks/run_checks.py", "--output", str(out),
             "--prompt", "tell the team where the docs live",
             cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "no_invented_urls" in r.stdout and "no_invented_quotes" in r.stdout


def test_single_output_default_checks_clean_green(tmp_path):
    # The positive half: clean prose under the default check list exits 0, which also
    # proves every id in the default list resolves (a typo'd default would exit 2).
    out = tmp_path / "out.txt"
    out.write_text("The demo moved to Thursday. Sam found the bug and fixed it the same afternoon.\n")
    r = _run("tests/checks/run_checks.py", "--output", str(out),
             cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 0, r.stdout + r.stderr


# --------------------------------------------------------------------------- dogfood

def test_dogfood_real_green():
    r = _run("tests/checks/dogfood.py", "--root", REPO, cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_dogfood_injected_slop_exits1(tmp_path):
    root = _copy(str(tmp_path / "repo"), "skills")
    ref = os.path.join(root, "skills", "voicestead", "references", "voice.md")
    with open(ref, "a", encoding="utf-8") as fh:
        fh.write("\n\nAt the end of the day, it’s worth noting that we must leverage synergy.\n")
    r = _run("tests/checks/dogfood.py", "--root", root, cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "DOGFOOD FAILED" in r.stdout


# --------------------------------------------------------------------------- check_placeholders

def test_check_placeholders_strict_exits1(tmp_path):
    # Build the sentinel at runtime so this test file doesn't trip the guard on itself.
    token = "REPLACE" + "_ME_OWNER"
    work = tmp_path / "workdir"
    work.mkdir()
    (work / "config.txt").write_text(f"owner = {token}\n")
    strict = _run("scripts/check_placeholders.py", "--strict", cwd=str(work))
    assert strict.returncode == 1, strict.stdout + strict.stderr
    assert token in strict.stdout
    # Report mode (no --strict) finds the same placeholder but exits 0.
    report = _run("scripts/check_placeholders.py", cwd=str(work))
    assert report.returncode == 0, report.stdout + report.stderr


# --------------------------------------------------------------------------- log_eval_run (the run ledger)

# One real mock benchmark, produced by the real orchestrator, shared by the ledger tests:
# the ledger's job is copying artifact numbers, so the artifact must be a real one.


@pytest.fixture(scope="module")
def mock_eval_out(tmp_path_factory):
    out = tmp_path_factory.mktemp("ledger") / "res"
    env = dict(os.environ, VOICESTEAD_MOCK="1")
    r = subprocess.run([sys.executable, os.path.join(REPO, "tests", "run_eval.py"),
                        "--cases", os.path.join(REPO, "tests", "cases.json"),
                        "--runs", "1", "--ids", "3", "--out", str(out)],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    return out


def _evals_dir(tmp_path):
    """A fresh ledger dir seeded with the real committed README (markers included)."""
    d = tmp_path / "evals"
    d.mkdir()
    shutil.copy2(os.path.join(REPO, "docs", "evals", "README.md"), str(d / "README.md"))
    return d


def _log(out_dir, evals_dir, *args):
    return _run("scripts/log_eval_run.py", str(out_dir), "--dir", str(evals_dir), *args)


def test_log_eval_run_copies_artifact_numbers(tmp_path, mock_eval_out):
    d = _evals_dir(tmp_path)
    r = _log(mock_eval_out, d, "--slug", "mock-rehearsal", "--notes", "pipeline rehearsal")
    assert r.returncode == 0, r.stdout + r.stderr

    bench = json.load(open(os.path.join(str(mock_eval_out), "benchmark.json")))
    date = bench["metadata"]["timestamp"][:10]
    entry_path = os.path.join(str(d), "%s-mock-rehearsal.md" % date)
    assert os.path.exists(entry_path)
    entry = open(entry_path).read()
    # every figure below is read back from the benchmark and matched verbatim -
    # copied, never computed
    win = bench["overall"]["win_rate"]
    assert "- **Backend:** mock" in entry
    assert ("- **Cases:** %s" % bench["overall"]["cases"]) in entry
    assert ("- **Blind win rate:** %s (%sW/%sT/%sL of %s valid)"
            % (win["rate"], win["wins"], win["ties"], win["losses"], win["n_valid"])) in entry
    assert "- **Tokens:** not reported by this backend" in entry  # mock never hits the seam
    assert "run_eval.py" in entry  # the exact command rode along from the metadata
    assert "pipeline rehearsal" in entry
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    assert ("- **Git commit:** %s" % head) in entry
    # the index regenerated: empty state replaced by a table row linking the entry
    readme = open(os.path.join(str(d), "README.md")).read()
    assert "No runs yet" not in readme
    assert ("%s-mock-rehearsal.md" % date) in readme


def test_log_eval_run_reports_usage_when_backend_reported_it(tmp_path, mock_eval_out):
    work = tmp_path / "res"
    shutil.copytree(str(mock_eval_out), str(work))
    bp = os.path.join(str(work), "benchmark.json")
    b = json.load(open(bp))
    b["metadata"]["backend"] = "claude-cli"
    b["metadata"]["llm_usage"] = {"calls": 8, "input_tokens": 88, "output_tokens": 56,
                                  "total_cost_usd": 0.008, "cost_reported": True}
    json.dump(b, open(bp, "w"))
    d = _evals_dir(tmp_path)
    r = _log(work, d, "--slug", "cli-run")
    assert r.returncode == 0, r.stdout + r.stderr
    date = b["metadata"]["timestamp"][:10]
    entry = open(os.path.join(str(d), "%s-cli-run.md" % date)).read()
    assert "- **Tokens:** 88 in / 56 out (8 calls)" in entry
    assert "- **Cost (USD):** 0.008" in entry


def test_log_eval_run_refuses_missing_field(tmp_path, mock_eval_out):
    # NEGATIVE-PATH CANARY: a benchmark without provenance must be refused whole -
    # no entry, no blank cell, no guessed value.
    work = tmp_path / "res"
    shutil.copytree(str(mock_eval_out), str(work))
    bp = os.path.join(str(work), "benchmark.json")
    b = json.load(open(bp))
    del b["metadata"]["backend"]
    json.dump(b, open(bp, "w"))
    d = _evals_dir(tmp_path)
    r = _log(work, d, "--slug", "bad-run")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "metadata.backend" in (r.stdout + r.stderr)
    assert os.listdir(str(d)) == ["README.md"]  # nothing half-written


def test_log_eval_run_requires_benchmark(tmp_path):
    empty = tmp_path / "res"
    empty.mkdir()
    r = _log(empty, _evals_dir(tmp_path), "--slug", "x")
    assert r.returncode == 1
    assert "benchmark.json" in (r.stdout + r.stderr)


def test_log_eval_run_refuses_readme_without_markers(tmp_path, mock_eval_out):
    d = tmp_path / "evals"
    d.mkdir()
    (d / "README.md").write_text("# a ledger with no index markers\n")
    r = _log(mock_eval_out, d, "--slug", "x")
    assert r.returncode == 1
    assert "marker" in (r.stdout + r.stderr).lower()
    assert os.listdir(str(d)) == ["README.md"]  # refused before writing the entry


def test_log_eval_run_refuses_duplicate_entry(tmp_path, mock_eval_out):
    d = _evals_dir(tmp_path)
    assert _log(mock_eval_out, d, "--slug", "twice").returncode == 0
    r = _log(mock_eval_out, d, "--slug", "twice")
    assert r.returncode == 1
    assert "already exists" in (r.stdout + r.stderr)


# --------------------------------------------------------------------------- per-section (run_checks --per-section)

_CLEAN_PAR = ("The vendor sent the corrected docs on Tuesday. We reran the import and "
              "the numbers matched. Nothing else changed for the team this week.")
_SLOP_PAR = ("We will leverage robust tooling to streamline the rollout, foster "
             "alignment, and elevate every seamless, transformative deliverable.")


def _drift_doc():
    """Six sections: a preamble, four clean parts, and a tell-dense LAST section.
    Enough clean prose (800 words measured by tm.word_count) dilutes the seven
    tell-words to 1.75/200w — under the 2.0 whole-doc threshold — while the last
    section alone sits at 7.0/200w over the check's 200-word floor. The drift
    this mode exists to catch."""
    parts = ["A handbook draft for the team."]
    for i in range(1, 5):
        parts.append("## Part %d\n\n%s" % (i, " ".join([_CLEAN_PAR] * 8)))
    parts.append("## Rollout\n\n%s" % _SLOP_PAR)
    return "\n\n".join(parts)


def test_per_section_catches_last_section_drift(tmp_path):
    # THE ASYMMETRY CANARY: the whole-doc frequency threshold passes; --per-section must fail.
    doc = tmp_path / "doc.md"
    doc.write_text(_drift_doc())
    checks_cwd = os.path.join(REPO, "tests", "checks")

    whole = _run("tests/checks/run_checks.py", "--output", str(doc),
                 "--checks", "tell_flags", cwd=checks_cwd)
    assert whole.returncode == 0, whole.stdout + whole.stderr
    assert '"soft_flags": 0' in whole.stdout  # diluted below threshold: reports clean

    per = _run("tests/checks/run_checks.py", "--output", str(doc), "--per-section",
               "--checks", "tell_flags", cwd=checks_cwd)
    assert per.returncode == 1, "drift signature failed to fire:\n" + per.stdout + per.stderr
    assert 'section 6/6 "Rollout"' in per.stdout   # index + heading in the failure line
    assert '"drift"' in per.stdout and '"tell_flags"' in per.stdout


def test_per_section_single_section_matches_whole_doc(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text(" ".join([_CLEAN_PAR] * 8))  # no H2 headings anywhere
    per = _run("tests/checks/run_checks.py", "--output", str(doc), "--per-section",
               "--checks", "tell_flags,no_high_conf_tells",
               cwd=os.path.join(REPO, "tests", "checks"))
    assert per.returncode == 0, per.stdout + per.stderr
    assert '"sections": 1' in per.stdout
    assert '"drift": []' in per.stdout


def test_per_section_hard_failure_exits1(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("## Update\n\nShip it Friday.\n\n## Close\n\n"
                   "It's worth noting that we should ship.")
    per = _run("tests/checks/run_checks.py", "--output", str(doc), "--per-section",
               "--checks", "no_high_conf_tells", cwd=os.path.join(REPO, "tests", "checks"))
    assert per.returncode == 1, per.stdout + per.stderr
    assert "[FAIL]" in per.stdout and '"Close"' in per.stdout


def test_per_section_rejects_corpus_mode():
    r = _run("tests/checks/run_checks.py", "--corpus", os.path.join(REPO, "tests", "corpus"),
             "--per-section", cwd=os.path.join(REPO, "tests", "checks"))
    assert r.returncode == 2, r.stdout + r.stderr


def test_per_section_keeps_whole_doc_hard_failures(tmp_path):
    # NEGATIVE-PATH CANARY for the whole-document rule: the lone inches-mark quote in
    # section 1 mispairs with the citation's opening quote in section 2, so the tell
    # is exposed at document scope (--output hard-fails) while each section passes in
    # isolation. --per-section must stay a superset of --output and exit 1 too.
    doc = tmp_path / "doc.md"
    doc.write_text('## Desk setup\n\nThe 24" ultrawide arrived and the stand fits the '
                   'rail.\n\n## Pricing feedback\n\nCut the line and keep the phrase '
                   '"when it comes to pricing, we lead" out of the deck.\n')
    checks_cwd = os.path.join(REPO, "tests", "checks")

    whole = _run("tests/checks/run_checks.py", "--output", str(doc),
                 "--checks", "no_high_conf_tells", cwd=checks_cwd)
    assert whole.returncode == 1, whole.stdout + whole.stderr  # the premise: --output gates

    per = _run("tests/checks/run_checks.py", "--output", str(doc), "--per-section",
               "--checks", "no_high_conf_tells", cwd=checks_cwd)
    assert per.returncode == 1, "whole-doc hard failure dropped:\n" + per.stdout + per.stderr
    assert '"whole_doc_hard_failures": 1' in per.stdout
    assert "whole-document hard failures:" in per.stdout


def test_per_section_grades_heading_text_too(tmp_path):
    # NEGATIVE-PATH CANARY for the heading-prepend rule: the only tells live in the
    # final H2 heading itself; a build that grades section bodies alone reports the
    # document clean and exits 0 instead of firing the drift signature.
    doc = tmp_path / "doc.md"
    clean = " ".join([_CLEAN_PAR] * 8)
    doc.write_text("## Part 1\n\n%s\n\n## Part 2\n\n%s\n\n"
                   "## Leveraging seamless synergy\n\nShip the update Friday.\n"
                   % (clean, clean))
    per = _run("tests/checks/run_checks.py", "--output", str(doc), "--per-section",
               "--checks", "tell_flags", cwd=os.path.join(REPO, "tests", "checks"))
    assert per.returncode == 1, "heading tells failed to gate:\n" + per.stdout + per.stderr
    assert '"Leveraging seamless synergy"' in per.stdout
    assert '"drift"' in per.stdout and '"tell_flags"' in per.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
