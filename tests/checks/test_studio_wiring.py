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


def test_studio_reference_covers_the_contract():
    md = _read("references/studio.md")
    # invariants
    assert "approved" in md.lower() and "log_draft" in md
    assert "reference" in md.lower() and "delimiters" in md.lower()   # truth-in-context
    # the full tool surface
    for tool in ["ping", "whoami", "get_voice_profile", "save_voice_profile",
                 "list_influence_cards", "save_influence_card", "get_writer_context",
                 "log_draft", "log_verdict", "score_draft", "get_writer_stats"]:
        assert tool in md, tool
    # every A4 error code has a designed state
    for code in ["unauthorized", "forbidden_scope", "invalid_input", "not_found",
                 "conflict", "limit_exceeded", "budget_exhausted", "quarantined", "internal"]:
        assert code in md, code
    # gated, honest backfill copy — never claims availability
    assert "coming soon" in md.lower() or "not yet" in md.lower() or "not live" in md.lower()


def test_studio_reference_never_promises_unshipped_features_as_live():
    md = _read("references/studio.md").lower()
    # a naive "you can now import your archive" claim would violate the honesty rule
    assert "you can now import" not in md
    assert "backfill is live" not in md


def test_voice_reference_has_wall_gated_offer_and_decline_marker():
    md = _read("references/voice.md")
    assert "Voicestead Memory" in md
    assert "mcp.voicestead.ai" in md
    assert "declined" in md.lower()          # the decline marker convention
    assert "at most once" in md.lower() or "one offer" in md.lower()


def test_step1_routes_to_studio_when_connected():
    md = _read("SKILL.md")
    # the load table should name studio.md as the connected-mode reference
    seg = md.split("## Step 1")[1].split("## The three mental models")[0]
    assert "studio.md" in seg


def test_connect_reference_covers_every_client_and_the_gotcha():
    md = _read("references/connect.md")
    # the connect endpoint and the Claude Code command
    assert "https://mcp.voicestead.ai/mcp" in md
    assert "claude mcp add" in md
    # all three client guides
    assert "claude.ai" in md.lower()
    assert "desktop" in md.lower()
    assert "Claude Code" in md
    # the #1 silent failure, called out
    assert "current" in md.lower() and "chat" in md.lower()
    assert "enable" in md.lower() or "turn" in md.lower()
    # ask ONE question when the client is unknown
    assert "Claude app, or Claude Code" in md
    # every guide hands off to the doctor
    assert md.count("ask me to check the connection") >= 3
    # the reconnect fixes the error states point to
    assert "re-sign-in" in md or "re-sign in" in md.lower()
    assert "permission" in md.lower()


def test_studio_has_the_doctor_with_verbatim_scope_labels():
    md = _read("references/studio.md")
    assert "ping" in md and "whoami" in md
    # the four app labels, verbatim
    for label in ["Read your memories", "Add to your memory",
                  "Use your voice profile", "See your receipts"]:
        assert label in md, label
    # the silent first check that drops to broken-connection behavior without announcing
    low = md.lower()
    assert "silent" in low
    assert "start" in low and "session" in low
