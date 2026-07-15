import os, sys
TESTS = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS)
import run_skill


def test_studio_context_is_embedded_as_reference_only():
    sys_prompt = run_skill.build_system(load=["references/studio.md"],
                                        studio_context="- past line: keep it short and plain")
    assert "keep it short and plain" in sys_prompt
    # it must be fenced as reference, not folded into instructions
    assert "writer_context" in sys_prompt.lower()
    assert "reference only" in sys_prompt.lower()


def test_no_studio_context_leaves_system_prompt_unchanged():
    a = run_skill.build_system(load=["references/voice.md"])
    b = run_skill.build_system(load=["references/voice.md"], studio_context=None)
    assert a == b


def test_connection_none_is_a_noop():
    # Local-mode protection: no simulated connection => byte-identical system prompt.
    base = run_skill.build_system(load=["references/studio.md"])
    assert run_skill.build_system(load=["references/studio.md"], connection=None) == base


def test_connection_renders_state_personas_and_error():
    sysp = run_skill.build_system(
        load=["references/studio.md"],
        connection={"state": "connected", "personas": ["Exec", "Personal"],
                    "default_persona": "Casual", "tool_error": "quarantined",
                    "identity": "jason@example.com", "scopes": ["Read your memories"]})
    assert "voicestead_memory_session" in sysp
    assert "Exec" in sysp and "Personal" in sysp and "Casual" in sysp
    assert "quarantined" in sysp
    assert "jason@example.com" in sysp and "Read your memories" in sysp


def test_connection_and_studio_context_compose():
    sysp = run_skill.build_system(connection={"personas": ["Exec"]},
                                  studio_context="- a past line the user liked")
    assert "voicestead_memory_session" in sysp and "writer_context" in sysp
