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


def test_error_section_states_retry_policy_and_global_rules():
    md = _read("references/studio.md")
    low = md.lower()
    # only limit_exceeded (rate) and internal retry — the policy is stated
    assert "retry" in low
    assert "limit_exceeded" in md and "internal" in md
    # the global no-leak / no-stall rules
    assert "raw code" in low or "raw error" in low
    assert "single retry" in low or "one retry" in low or "beyond a single retry" in low
    # quarantined framed as the product working, pointing at the app
    assert "app.voicestead.ai" in md
    # budget_exhausted goes silent unless asked
    assert "budget_exhausted" in md


def test_free_cap_is_the_only_extra_paid_mention_and_is_gated():
    studio = _read("references/studio.md")
    voice = _read("references/voice.md")
    # the free-cap paid line exists exactly once, inside the free-cap context
    assert studio.count("raises the cap") == 1
    idx = studio.index("free memory cap")
    assert "raises the cap" in studio[idx:idx + 800]
    # it is not duplicated as a free-floating upsell in the wall-offer file
    assert "raises the cap" not in voice
    # spec 6c: exactly two gated paid mentions across the WHOLE skill — the
    # wall-gated offer (voice.md) and this free-cap line (studio.md). Prove no
    # third free-cap upsell hides in any other file: the phrasing occurs exactly
    # once skill-wide, and only in studio.md.
    import os
    total = 0
    for root, _, files in os.walk(SKILL):
        for name in files:
            if name.endswith(".md"):
                n = open(os.path.join(root, name), encoding="utf-8").read().count("raises the cap")
                total += n
                if n:
                    assert name == "studio.md", "unexpected free-cap upsell in %s" % name
    assert total == 1, "expected exactly one free-cap paid mention skill-wide, found %d" % total


def test_router_covers_all_five_states_terse_and_before_step0():
    md = _read("SKILL.md")
    router = md[:md.index("## Step 0: Pick the mode")]
    low = router.lower()
    # the three visible states in the always-loaded file (broken/limited fold under connected)
    assert "local" in low and "curious" in low and "connected" in low
    # routes to both references, gated
    assert "references/connect.md" in router
    assert "references/studio.md" in router
    # curiosity trigger + local-stance preserved
    assert "memory" in low
    assert "proceed exactly as today, byte-for-byte" in md
    assert "Never call a Studio tool that isn't present" in md
    # Step 1 connect row now points at connect.md, not voice.md, for the mechanics
    step1 = md[md.index("## Step 1"):md.index("## The three mental models")]
    assert "references/connect.md" in step1
