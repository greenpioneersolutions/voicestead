"""Regression fixture: a State-1 (local) session must read identical drafting bytes.

The connection-model change rewrites SKILL.md's Step 0 router and repoints one Step-1
connect row. It must NOT touch the bytes a local session acts on: the Step 0 mode
definitions and everything from the three mental models to end of file. This test
freezes those regions and pins the local-mode stance strings. Offline, deterministic,
no API key.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL = os.path.join(REPO, "skills", "voicestead", "SKILL.md")
SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "skill_local_behavior.snapshot.md")

# The nine writing-job routing rows a local session uses (Step 1). Connection rows
# (studio.md, connect.md) are intentionally excluded — they may change.
WRITING_JOB_REFS = ["persuasion.md", "influence.md", "formats.md", "tells.md",
                    "coaching.md", "capture.md", "inspiration.md", "science.md", "voice.md"]

BOUNDARY = "\n<<<REGION-BOUNDARY>>>\n"


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _regions(md):
    """The two drafting-behavior regions this change must never touch."""
    a = md[md.index("## Step 0: Pick the mode"):md.index("## Step 1")]
    b = md[md.index("## The three mental models"):]
    return a, b


def _snapshot_text(md):
    a, b = _regions(md)
    return a + BOUNDARY + b


def test_drafting_regions_are_byte_identical_to_snapshot():
    current = _snapshot_text(_read(SKILL))
    frozen = _read(SNAPSHOT)
    assert current == frozen, (
        "SKILL.md drafting behavior changed (Step 0 modes or mental-models-to-EOF). "
        "If intentional, regenerate the snapshot; if not, revert."
    )


def test_every_writing_job_route_survives():
    md = _read(SKILL)
    step1 = md[md.index("## Step 1"):md.index("## The three mental models")]
    for ref in WRITING_JOB_REFS:
        assert "references/%s" % ref in step1, "Step 1 lost the %s route" % ref


def test_local_mode_stance_strings_present():
    md = _read(SKILL)
    assert "local mode" in md.lower()
    assert "proceed exactly as today, byte-for-byte" in md
    assert "Never call a Studio tool that isn't present" in md


def test_skill_md_confines_studio_to_the_router():
    # Self-contained read (no dependence on the module's helpers): Studio *substance*
    # must live in the connected-only references, never the always-loaded SKILL.md.
    import os
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md = open(os.path.join(repo, "skills", "voicestead", "SKILL.md"), encoding="utf-8").read()
    low = md.lower()
    assert "mcp.voicestead.ai" not in md
    assert "claude mcp add" not in md
    assert "get_voice_profile" not in md
    assert "## the doctor" not in low
    assert "budget_exhausted" not in md and "forbidden_scope" not in md   # no error table
    assert "## personas" not in low
