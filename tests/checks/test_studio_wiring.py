import os
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL = os.path.join(REPO, "skills", "voicestead")


def _read(rel):
    return open(os.path.join(SKILL, rel), encoding="utf-8").read()


def test_skill_has_connected_precondition_hook():
    md = _read("SKILL.md")
    assert "Voicestead Memory" in md
    assert "references/studio.md" in md
    # the hook must sit BEFORE mode selection so detection happens first
    assert md.index("references/studio.md") < md.index("## Step 0: Pick the mode")


def test_local_mode_is_the_default_stance():
    md = _read("SKILL.md")
    assert "local mode" in md.lower()
    assert "never call a Studio tool that isn't present" in md.lower() or \
           "never call a studio tool that isn't present" in md.lower()
