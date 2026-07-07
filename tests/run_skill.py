#!/usr/bin/env python3
"""Invoke Claude WITH and WITHOUT the skill, so outputs can be graded.

Faithful-enough progressive disclosure: the system prompt = SKILL.md, plus any reference
files a case names in `load` (mirroring what Claude would pull in for that job). For maximum
fidelity you can instead drive the installed skill through the Claude Agent SDK; this
single-turn path is chosen for portability and zero setup in CI.

Generation routes through tests/llm_backend.py. The default backend (claude-cli) drives
the installed `claude` binary on a Claude Code subscription - no ANTHROPIC_API_KEY.
`--backend api` (or VOICESTEAD_BACKEND=api) uses the Anthropic SDK path and needs the
key. Model via --model or $SKILL_MODEL. Set VOICESTEAD_MOCK=1 for a keyless run: run()
returns deterministic canned text (varying by prompt) and no backend is ever invoked.

Guards (enforced in llm_backend for both real backends): a generation that stops for any
reason other than a normal end of turn (max_tokens truncation, refusal), or that carries
no text, RAISES instead of returning - an empty or truncated output must never be graded.
`temperature` is only sent when explicitly set; several current models reject
non-default sampling parameters, so the default is to omit it. The claude-cli backend
cannot set temperature at all and raises rather than silently ignoring it.

Mock knobs (test-only, require VOICESTEAD_MOCK=1):
  VOICESTEAD_MOCK_REVIEW_REWRITE=1  review-mode prompts return the quoted source verbatim
                                    (deliberately violates not_a_rewrite, for gate tests)
  VOICESTEAD_MOCK_BLOAT=1           improve-mode prompts return a padded output
                                    (deliberately violates length_delta_max)
  VOICESTEAD_MOCK_DRIFT=1           handbook prompts get a tell-dense final section
                                    (deliberately violates per_section_tell_rise_max,
                                    for gate tests)
"""
import argparse, hashlib, os, re, sys

TESTS = os.path.dirname(os.path.abspath(__file__))
if TESTS not in sys.path:
    sys.path.insert(0, TESTS)
import llm_backend

MOCK = os.environ.get("VOICESTEAD_MOCK", "") not in ("", "0")

MODEL = os.environ.get("SKILL_MODEL", "claude-sonnet-5")
REPO = os.path.dirname(TESTS)
SKILL_DIR = os.path.join(REPO, "skills", "voicestead")


def build_system(load=None):
    parts = [open(os.path.join(SKILL_DIR, "SKILL.md")).read()]
    for rel in (load or []):
        path = os.path.join(SKILL_DIR, rel)
        if os.path.exists(path):
            parts.append("\n\n<loaded_reference path='%s'>\n%s\n</loaded_reference>" % (rel, open(path).read()))
    return "\n".join(parts)


# ---------- mock seam (VOICESTEAD_MOCK=1): deterministic canned outputs, zero network ----------

_MOCK_TOPICS = ["launch", "sprint", "rollout", "handoff", "review", "deploy",
                "retro", "offsite", "migration", "standup"]

# The no-skill baseline always carries this opener so (a) Tier-1 shows a with/without
# pass-rate delta and (b) the mock judge can recognize the baseline side blind.
_MOCK_SLOP = ("I hope this message finds you well. I just wanted to reach out and touch base "
              "about the {topic}. In today's rapidly evolving landscape, staying aligned is key, "
              "and I wanted to circle back, follow up, and check in on next steps. Please do not "
              "hesitate to reach out with any questions.")


def _mock_output(prompt, with_skill):
    h = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8], 16)
    topic = _MOCK_TOPICS[h % len(_MOCK_TOPICS)]
    if not with_skill:
        return _MOCK_SLOP.format(topic=topic)
    low = prompt.lower()
    m = re.search(r":\s*'(.+)'", prompt, re.S)  # the quoted material after "edit this:" etc.
    quoted = m.group(1).strip() if m else ""
    if "handbook" in low and "section" in low:
        # the anti-drift metamorphic case: a long multi-section document. Clean voice
        # in every section; VOICESTEAD_MOCK_DRIFT=1 turns the LAST section sloppy,
        # which must trip the per_section_tell_rise_max gate.
        section = ("Keep this part short. Ask the person who ran it last time before "
                   "you change anything, and write down what surprised you.")
        parts = ["## %s\n\n%s" % (name, section)
                 for name in ("Onboarding", "Standups", "Shipping", "Incidents", "Retros")]
        if os.environ.get("VOICESTEAD_MOCK_DRIFT", "") not in ("", "0"):
            parts[-1] += ("\n\nWe will leverage robust, seamless tooling to streamline "
                          "and elevate every deliverable going forward.")
        return "A short handbook for the team.\n\n" + "\n\n".join(parts)
    if re.search(r"\bfeedback\b|\breview\b|don'?t rewrite", low):
        if os.environ.get("VOICESTEAD_MOCK_REVIEW_REWRITE", "") not in ("", "0") and quoted:
            return quoted  # deliberate Review-mode violation, for must_pass gate tests
        return ("Strongest move: the concrete lesson near the top - keep it. One question: who is "
                "this for, and what should they do after reading? One fix: end on the lesson, "
                "not a question. Ship after that.")
    if quoted and re.search(r"\b(edit|tighten|improve|humanize|make this|fix this|better)\b", low):
        out = quoted  # restrained improve: the text was already fine
        if re.search(r"in today'?s|worth noting|at the end of the day|rapidly evolving", out, re.I):
            # the quoted text is slop; return a clean replacement instead of echoing it
            out = ("Our platform puts the team's work in one place. Adoption is growing. "
                   "Real numbers land Friday - if you want specifics sooner, ask me.")
        if os.environ.get("VOICESTEAD_MOCK_BLOAT", "") not in ("", "0"):
            out += (" Also, a longer meditation on process: we should honor the craft, revisit "
                    "our assumptions, and reflect at length on what this small change means for "
                    "every stakeholder in the wider organization going forward, together.")
        return out
    return ("Team: the %s plan moved and the new time is on the calendar. "
            "Nothing else changes. Questions to me." % topic)


# ---------- generation ----------

def run(prompt, with_skill=True, load=None, temperature=None, model=None, backend=None):
    """Generate one output. `temperature=None` (the default) omits the parameter entirely.
    `backend=None` resolves via llm_backend (flag > VOICESTEAD_BACKEND > claude-cli)."""
    if MOCK:
        text = _mock_output(prompt, with_skill)
        if not text.strip():
            raise RuntimeError("mock generation returned empty text")
        return text
    return llm_backend.complete(prompt, model=model or MODEL,
                                system=build_system(load) if with_skill else None,
                                max_tokens=4000, temperature=temperature, backend=backend)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--no-skill", action="store_true")
    ap.add_argument("--load", default="", help="comma-separated reference files to include")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--temperature", type=float, default=None,
                    help="omit to use the model's default (some models reject non-default values)")
    ap.add_argument("--backend", default=None, choices=llm_backend.BACKENDS,
                    help="claude-cli (default; runs on your Claude Code subscription) or "
                         "api (Anthropic SDK, needs ANTHROPIC_API_KEY)")
    args = ap.parse_args()
    prompt = open(args.prompt).read() if os.path.exists(args.prompt) else args.prompt
    load = [x.strip() for x in args.load.split(",") if x.strip()]
    print(run(prompt, with_skill=not args.no_skill, load=load, temperature=args.temperature,
              model=args.model, backend=args.backend))


if __name__ == "__main__":
    main()
