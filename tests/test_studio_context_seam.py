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
