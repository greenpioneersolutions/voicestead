"""Unit tests for the deterministic checks — they guard the guards.

The corpus fixtures prove the checks work end-to-end; these prove each check's logic
directly, so a regression in the math (burstiness CV, triad counting, number extraction)
can't slip through by happening to pass the corpus. Every false positive and false
negative the adversarial audit demonstrated is pinned here with its exact probe input.

  python -m pytest tests/checks/test_text_metrics.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_metrics as tm

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def one(text, check, **kw):
    """Run a single check and return its result dict."""
    cid = check if isinstance(check, str) else check["id"]
    return {r["id"]: r for r in tm.run(text, [check], **kw)}[cid]


# ---- _normalize (unicode punctuation) ----
def test_normalize_maps_curly_quotes():
    assert tm._normalize("’‘“”") == "''\"\""


def test_normalize_keeps_dashes():
    # em/en dashes are a legitimate style element, never rewritten
    assert tm._normalize("wait — now – go") == "wait — now – go"


# ---- no_invented_numbers (the hard Truth gate) ----
def test_invented_number_is_flagged():
    assert not one("We saw 47% growth this year.", "no_invented_numbers")["passed"]


def test_number_present_in_prompt_passes():
    assert one("We saw 47% growth.", "no_invented_numbers", prompt="growth hit 47% in Q3")["passed"]


def test_bracketed_placeholder_passes():
    assert one("We saw [X]% growth.", "no_invented_numbers")["passed"]


def test_bare_small_int_still_exempt():
    # 1-9 as bare counts/ordinals are structural, never treated as fabricated
    assert one("Here are 3 options.", "no_invented_numbers")["passed"]


def test_small_percent_is_flagged():
    # audit probe: single-digit percentages were exempt because '%' was stripped early
    assert not one("Adoption jumped 9% after the change.", "no_invented_numbers",
                   prompt="say adoption improved")["passed"]


def test_small_dollar_is_flagged():
    assert not one("This saves $8 per seat.", "no_invented_numbers")["passed"]


def test_small_dollar_millions_flagged():
    assert not one("The $9M budget is approved.", "no_invented_numbers")["passed"]


def test_five_percent_lift_flagged():
    assert not one("We expect a 5% lift.", "no_invented_numbers")["passed"]


def test_small_decimal_flagged():
    assert not one("Churn fell 9.0% this month.", "no_invented_numbers")["passed"]


def test_source_numbers_not_invented():
    # audit probe: truthful review feedback hard-failed because source= was ignored
    assert one("You cite 14 incidents but no period.", "no_invented_numbers",
               source="We had 14 incidents last quarter.")["passed"]


def test_spelled_prompt_number_licenses_digits():
    assert one("We logged 14 incidents.", "no_invented_numbers",
               prompt="we had fourteen incidents")["passed"]


def test_spelled_compound_licenses_digits():
    assert one("We saw 73% adoption.", "no_invented_numbers",
               prompt="seventy-three percent of the team adopted it")["passed"]


def test_spelled_range_licenses_digits():
    assert one("Plan for 10-20 users.", "no_invented_numbers",
               prompt="ten to twenty users")["passed"]


def test_spelled_word_not_consumed_by_neighbor():
    # 'exactly two' must license 2 even when 'two' follows a non-number word
    assert one("We had 2 outages.", "no_invented_numbers",
               prompt="we saw exactly two big outages")["passed"]


def test_spelled_source_number_licenses_digits():
    assert one("Both of the 11 findings stand.", "no_invented_numbers",
               source="the report listed eleven findings")["passed"]


def test_md_link_text_numbers_not_hidden():
    # audit probe: '[...47%...](url)' was deleted as a placeholder, hiding the figure
    assert not one("[We saw 47% growth](https://x.example) and it compounds.",
                   "no_invented_numbers")["passed"]


def test_year_not_in_input_flagged():
    # honest behavior: years get no special exemption
    assert not one("The plan ships in 2026.", "no_invented_numbers")["passed"]


def test_comma_number_licensed_by_prompt():
    assert one("The $2,400 quote stands.", "no_invented_numbers",
               prompt="vendor quoted $2,400")["passed"]


# ---- no_high_conf_tells (hard) ----
def test_high_conf_tell_fires():
    assert not one("In today's rapidly evolving landscape, we ship.", "no_high_conf_tells")["passed"]


def test_clean_prose_passes_tells():
    assert one("We ship Tuesday. The vendor docs were wrong.", "no_high_conf_tells")["passed"]


def test_literal_end_of_day_ok():
    # audit probe: the literal deadline sense must not hard-fail
    assert one("Send the numbers at the end of the day Friday.", "no_high_conf_tells")["passed"]


def test_discourse_end_of_day_flagged():
    assert not one("At the end of the day, what matters is trust.", "no_high_conf_tells")["passed"]


def test_quoted_tell_in_feedback_ok():
    # audit probe: quoting the slop you cut is citation, not slop
    assert one('Cut the opener — "in today\'s rapidly evolving landscape" says nothing. '
               "Open with the date instead.", "no_high_conf_tells")["passed"]


def test_colon_in_conclusion_flagged():
    assert not one("In conclusion: ship it.", "no_high_conf_tells")["passed"]


def test_tell_across_linebreak_flagged():
    assert not one("It's worth\nnoting that we slipped.", "no_high_conf_tells")["passed"]


def test_curly_apostrophe_tell_flagged():
    # session find: ’ variants of every tell passed before _normalize
    assert not one("It’s worth noting that we slipped.", "no_high_conf_tells")["passed"]


def test_curly_todays_tell_flagged():
    assert not one("In today’s fast-paced world, we ship.", "no_high_conf_tells")["passed"]


def test_apostrophe_less_todays_flagged():
    assert not one("In todays fast-paced world, we ship.", "no_high_conf_tells")["passed"]


# ---- tell_flags (inflections) ----
def test_inflected_tells_counted():
    r = one("The plan delves into costs and leverages our stack seamlessly.", "tell_flags")
    assert "delve" in r["detail"] and "leverage" in r["detail"] and "seamless" in r["detail"]


def test_more_inflections_counted():
    r = one("It utilizes the audit trail, fosters trust, and underscored the risk.", "tell_flags")
    assert "utilize" in r["detail"] and "foster" in r["detail"] and "underscore" in r["detail"]
    assert not r["passed"]


def test_no_overmatch_on_similar_words():
    r = one("The dell veered left near the harbor.", "tell_flags")
    assert r["detail"] == "no category tell-words"


def test_plural_synergies_counted():
    assert "synergy" in one("We found synergies across both teams.", "tell_flags")["detail"]


def test_single_contextual_tell_in_short_text_passes():
    # 200-word floor: one literal-sense tell-word in a short note (or a short
    # section under per-section grading) is the judge's call, not a failure
    r = one("We signed the papers to become foster parents.", "tell_flags")
    assert r["passed"], r
    assert r["metric"] == 1.0  # one tell over the 200-word floor


def test_tell_cluster_in_short_text_still_fails():
    # NEGATIVE-PATH CANARY: the floor must not wave a genuine cluster through
    r = one("We leverage robust seamless synergy to streamline delivery.", "tell_flags")
    assert not r["passed"], r


# ---- formula_structures ----
def test_formula_false_contrast_fires():
    assert not one("It's not just speed, it's trust.", "formula_structures")["passed"]


def test_formula_curly_apostrophe_fires():
    assert not one("It’s not just speed, it’s trust.", "formula_structures")["passed"]


def test_formula_across_linebreak_fires():
    assert not one("Here's\nthe thing about the launch.", "formula_structures")["passed"]


# ---- burstiness / split_sentences ----
def test_metronomic_rhythm_flagged():
    t = "The team ships code fast. The team writes tests well. The team helps each other. The team meets each day."
    assert not one(t, "burstiness_ok")["passed"]


def test_varied_rhythm_passes():
    t = ("We shipped. It took three weeks of careful, sometimes maddening work to get the migration "
         "right, and the vendor docs fought us the entire way. Then it worked.")
    assert one(t, "burstiness_ok")["passed"]


def test_bulleted_metronome_flagged():
    # audit probe: bullet slop used to collapse to one 'sentence' and auto-pass
    t = ("The plan:\n- we align on the goals and the metrics\n- we deliver the features and the tests\n"
         "- we improve the process and the tooling\n- we celebrate the wins and the growth\nDone.")
    assert not one(t, "burstiness_ok")["passed"]


def test_no_bare_list_number_sentences():
    s = tm.split_sentences("Two asks. 1. Fund the SRE. 2. Backfill on-call. 3. Revisit in March.")
    assert not any(x.strip() in {"1.", "2.", "3."} for x in s)


def test_lowercase_voice_gets_split():
    s = tm.split_sentences("hey — pushing our 1:1 to thurs. something came up. same time.")
    assert len(s) == 3


def test_markdown_markers_stripped_in_sentences():
    s = tm.split_sentences("# Update\n- ship the fix\n- test it\nDone.")
    assert s and all(not x.startswith(("#", "-", "*")) for x in s)


def test_md_link_target_not_in_sentences():
    s = tm.split_sentences("See [the plan](https://example.com/plan). It ships Friday.")
    assert "https" not in " ".join(s)


def test_abbreviations_do_not_split():
    s = tm.split_sentences("Use the vendor keys, e.g. the sandbox ones. Then rotate them.")
    assert len(s) == 2


# ---- triads (rule of three) ----
def test_two_triads_flagged():
    t = ("The team is committed, the team is capable, and the team is resilient. "
         "We will streamline delivery, foster alignment, and elevate outcomes.")
    assert not one(t, "triads_ok")["passed"]


def test_single_triad_reported_not_failed():
    # rate floor: one legit enumeration in a short text is a report, not a failure
    r = one("It is faster, cheaper, and simpler.", "triads_ok")
    assert r["passed"] and "1 triad" in r["detail"]


def test_appositive_not_a_triad():
    r = one("I talked to Sam, who runs infra, and we agreed on next steps.", "triads_ok")
    assert r["detail"] == "no triads"


def test_oxford_less_triad_detected():
    assert "1 triad" in one("The new flow is faster, cheaper and simpler for everyone.",
                            "triads_ok")["detail"]


def test_vertical_list_not_a_triad():
    t = "Bring these to the offsite:\n- laptops,\n- badges, and\n- patience.\nSee you there."
    assert one(t, "triads_ok")["detail"] == "no triads"


# ---- no_throatclear_open ----
def test_throatclear_open_flagged():
    assert not one("I'm writing to let you know the demo moved.", "no_throatclear_open")["passed"]


def test_throatclear_behind_subject():
    # audit probe: a Subject: line used to hide the throat-clear entirely
    assert not one("Subject: Demo moved\n\nI'm writing to let you know the demo moved.",
                   "no_throatclear_open")["passed"]


def test_greeting_with_name_throatclear():
    assert not one("Hi Mark, I just wanted to check in on the launch.", "no_throatclear_open")["passed"]


def test_greeting_own_line_throatclear():
    assert not one("Hi Mark,\n\nI just wanted to check in on the launch.", "no_throatclear_open")["passed"]


def test_bold_greeting_throatclear():
    assert not one("**Hi team,** I just wanted to share an update.", "no_throatclear_open")["passed"]


def test_greeting_dash_checking_in_flagged():
    assert not one("Hey team — just checking in on the launch.", "no_throatclear_open")["passed"]


def test_curly_im_writing_flagged():
    assert not one("I’m writing to share an update.", "no_throatclear_open")["passed"]


def test_lowercase_voice_open_ok():
    # audit probe: the skill's own lowercase voice must not be punished
    assert one("hey — pushing our 1:1 to thurs, something came up. same time.",
               "no_throatclear_open")["passed"]


def test_on_point_open_passes():
    assert one("The demo moved to Thursday.", "no_throatclear_open")["passed"]


def test_subject_only_output_passes():
    assert one("Subject: Update", "no_throatclear_open")["passed"]


# ---- word_count / max_words / has_subject ----
def test_urls_dont_inflate_word_count():
    assert tm.word_count("see [the calendar](https://internal.example.com/cal/team-standup-v2) now") == 4


def test_bare_url_not_counted():
    assert tm.word_count("ship it https://example.com/x today") == 3


def test_max_words_with_link_counts_human_words():
    r = one("Quick note: check [the doc](https://x.example/d) before standup today.",
            {"id": "max_words", "params": {"limit": 9}})
    assert r["passed"] and r["metric"] == 8


def test_bold_subject_detected():
    assert one("**Subject:** Update", "has_subject")["passed"]


def test_plain_subject_detected():
    assert one("Subject: Migration slipping\n\nBody here.", "has_subject")["passed"]


def test_no_subject_line_fails():
    assert not one("No subject here, just the body of a note.", "has_subject")["passed"]


# ---- not_a_rewrite (Review-mode guard) ----
def test_feedback_is_not_a_rewrite():
    src = "After six months building our platform I learned shipping fast matters less than shipping right."
    fb = "The strongest line is 'shipping right' — keep it. Two questions: who is this for, and what's the ask?"
    assert one(fb, {"id": "not_a_rewrite"}, source=src)["passed"]


def test_wholesale_rewrite_is_flagged():
    src = "After six months building our platform I learned shipping fast matters less than shipping right."
    rewrite = "After six months building our platform, I learned that shipping fast matters less than shipping right."
    assert not one(rewrite, {"id": "not_a_rewrite"}, source=src)["passed"]


def test_quoting_review_passes():
    # audit probe: a case-4-conformant review that quotes the post scored 89% and failed
    src = ("After 6 months building our platform, I learned that shipping fast matters less than "
           "shipping right. We rushed v1 and paid for it. Here are 3 lessons: test early, listen "
           "to users, and stay humble. What do you think?")
    fb = ('Strongest line: "shipping fast matters less than shipping right" — keep it. '
          "Who is this for, and what should they do after reading?")
    assert one(fb, {"id": "not_a_rewrite"}, source=src)["passed"]


def test_single_quoted_span_stripped():
    src = ("After 6 months building our platform, I learned that shipping fast matters less than "
           "shipping right. We rushed v1 and paid for it. Here are 3 lessons: test early, listen "
           "to users, and stay humble. What do you think?")
    fb = "Your line 'shipping fast matters less than shipping right' lands. Cut the rest."
    assert one(fb, {"id": "not_a_rewrite"}, source=src)["passed"]


def test_tiny_source_guard():
    assert one("Don't ship it Friday. Wait for the soak test.", {"id": "not_a_rewrite"},
               source="Ship it Friday.")["passed"]


def test_no_source_passes():
    assert one("Any feedback at all.", {"id": "not_a_rewrite"})["passed"]


# ---- no_onboarding_pitch (the offer-once rule, made countable) ----
def test_onboarding_pitch_fires():
    assert not one("Here you go. Want to do a 3-minute voice setup?", "no_onboarding_pitch")["passed"]


def test_no_onboarding_pitch_clean():
    assert one("Here's your email. Send it when you're ready.", "no_onboarding_pitch")["passed"]


def test_requested_setup_not_a_nag():
    # audit probe: answering an explicit setup request is responsive, not a nag
    assert one("Sure — the voice setup takes three minutes.", "no_onboarding_pitch",
               prompt="can we do the voice setup?")["passed"]


def test_unrequested_pitch_still_fires_with_prompt():
    assert not one("Done. Want to build a voice profile?", "no_onboarding_pitch",
                   prompt="move the demo to Thursday")["passed"]


# ---- zombie_nouns (new) ----
def test_zombie_pileup_flagged():
    t = ("The implementation of the migration required the utilization of new tooling. "
         "The provision of training and the facilitation of onboarding remain open items.")
    assert not one(t, "zombie_nouns")["passed"]


def test_plain_prose_passes_zombie():
    assert one("We moved the demo to Thursday. Sam found the bug and fixed it the same afternoon.",
               "zombie_nouns")["passed"]


def test_common_nominalizations_within_threshold():
    # everyday nominalizations are counted, but plain prose stays under the bar
    assert one("Thanks for the information about the conference. The documentation is ready.",
               "zombie_nouns")["passed"]


def test_zombie_metric_reported():
    r = one("The evaluation of the proposal awaits the completion of the review, the "
            "submission of the assessment, and the finalization of the allocation.", "zombie_nouns")
    assert r["metric"] is not None and r["metric"] > 3.0 and not r["passed"]


def test_short_words_not_nominalizations():
    assert one("The city has a vision for unity.", "zombie_nouns")["detail"] == "no nominalization pileup"


# ---- false_agency (new) ----
def test_data_tells_flagged():
    assert not one("The data tells us we should ship.", "false_agency")["passed"]


def test_numbers_show_flagged():
    assert not one("The numbers show we missed the target.", "false_agency")["passed"]


def test_document_outlines_flagged():
    assert not one("This document outlines the plan for Q3.", "false_agency")["passed"]


def test_report_argues_flagged():
    assert not one("The report argues for a slower rollout.", "false_agency")["passed"]


def test_decision_emerged_flagged():
    assert not one("The decision emerged after the offsite.", "false_agency")["passed"]


def test_human_subject_passes_agency():
    assert one("Sam says the numbers are wrong, and we decided to ship anyway.", "false_agency")["passed"]


def test_plain_dashboard_reference_passes():
    # precision: neutral descriptions of artifacts are normal English
    assert one("The dashboard shows three failing checks.", "false_agency")["passed"]


# ---- run() contract ----
def test_unknown_check_id_raises():
    with pytest.raises(ValueError):
        tm.run("anything", ["no_invented_numers"])


def test_unknown_dict_check_id_raises():
    with pytest.raises(ValueError):
        tm.run("anything", [{"id": "nope", "params": {}}])


def test_run_normalizes_curly_input():
    r = tm.run("In today’s rapidly evolving landscape, we ship.", ["no_high_conf_tells"])
    assert not r[0]["passed"]


def test_registry_has_new_checks():
    assert "zombie_nouns" in tm.REGISTRY and "false_agency" in tm.REGISTRY


# ---- TELL_WORDS <-> tells.md sync (the code list mirrors the shipped catalog) ----
def test_tell_words_mirror_tells_md():
    tells_md = open(os.path.join(REPO, "skills", "voicestead", "references", "tells.md"), encoding="utf-8").read().lower()
    missing = [w for w in tm.TELL_WORDS if w.lower() not in tells_md]
    assert missing == [], "TELL_WORDS entries absent from tells.md: %s" % missing


# ---- split_sections (markdown H2 splitter for the drift guard) ----
def test_split_sections_basic():
    doc = "intro line\n\n## Alpha\n\na body.\n\n## Beta\n\nb body."
    assert tm.split_sections(doc) == [("", "intro line"), ("Alpha", "a body."), ("Beta", "b body.")]


def test_split_sections_fenced_h2_is_content():
    # THE SPLITTER CANARY: a '## ' line inside a code fence is content, not a boundary
    doc = "## Alpha\n\nbefore.\n\n```\n## not a heading\n```\n\nafter."
    secs = tm.split_sections(doc)
    assert [h for h, _ in secs] == ["Alpha"]
    assert "## not a heading" in secs[0][1]


def test_split_sections_tilde_fence():
    doc = "## Alpha\n\n~~~\n## still code\n~~~\n\n## Beta\n\nb."
    assert [h for h, _ in tm.split_sections(doc)] == ["Alpha", "Beta"]


def test_split_sections_mixed_fence_chars_do_not_close():
    # ~~~ lines inside a ``` fence are content, not closers: the fenced '## ' line
    # must stay content even after two tilde lines
    doc = "## Alpha\n\ntext.\n\n```\n~~~\n## fenced line\n~~~\n```\n\n## Beta\n\nb."
    secs = tm.split_sections(doc)
    assert [h for h, _ in secs] == ["Alpha", "Beta"]
    assert "## fenced line" in secs[0][1]


def test_split_sections_longer_fence_contains_shorter():
    # a four-backtick fence documenting a ``` example: the inner three-backtick
    # runs are too short to close the outer fence, so '## fake' never splits
    doc = "## Docs\n\n````\n```\n## fake\n```\n````\n\n## Real\n\nr."
    secs = tm.split_sections(doc)
    assert [h for h, _ in secs] == ["Docs", "Real"]
    assert "## fake" in secs[0][1]


def test_split_sections_indented_backticks_are_not_a_fence():
    # four-space indentation makes an indented code block, not a fence; a literal
    # backtick run there must not open phantom fence state that swallows headings
    doc = "## One\n\nbody.\n\n    ```\n\n## Two\n\nt."
    assert [h for h, _ in tm.split_sections(doc)] == ["One", "Two"]


def test_split_sections_no_headings_single_section():
    # single-section docs behave exactly as before: one section, the whole text
    assert tm.split_sections("no headings at all.") == [("", "no headings at all.")]


def test_split_sections_h3_and_nospace_do_not_split():
    assert [h for h, _ in tm.split_sections("### deep\nnot h2")] == [""]
    assert [h for h, _ in tm.split_sections("##nospace\nx")] == [""]


def test_split_sections_first_line_heading():
    assert tm.split_sections("## First\n\nonly section") == [("First", "only section")]


def test_split_sections_empty_text():
    assert tm.split_sections("") == [("", "")]
