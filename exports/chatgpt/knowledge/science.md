# The Evidence Base

The research behind Voicestead's rules. This file is NOT loaded for everyday writing jobs — load it when the person asks *why* a rule exists, wants the studies behind a claim, wants to go technically deeper, or challenges the skill's advice. It also exists to keep the skill honest: every operative rule traceable to its evidence, every evidence entry marked by how well we've verified it.

**Status legend:** ✔ *verified at source* (abstract/paper read during research) · ◇ *training-sourced* (well-established but re-verify before quoting numbers publicly).

## 1. Clarity and fluency — plain words make the author look smarter

✔ Oppenheimer (2006), *Applied Cognitive Psychology*: five experiments found a negative relationship between vocabulary complexity and judged intelligence, holding regardless of text quality; effect mediated by processing fluency — even hard-to-read fonts lowered judgments of the author. ✔ Alter & Oppenheimer (2009), *Personality and Social Psychology Review*: fluency is a general metacognitive cue — people judge easily-processed information as more true, across conceptual, perceptual, and linguistic forms.
◇ Related: jargon reduces processing fluency and engagement (Shulman et al., 2020); less-readable corporate filings correlate with worse informational outcomes (Li, 2008, *J. Accounting & Economics*).
**Feeds:** Model 3 (say it to one person), the quality bar's Clear rule, tells.md's plain-word swaps. The upgrade fluency research adds: readers aren't just slowed by complexity — they downgrade *the author*.

## 2. Concreteness — specifics signal listening

✔ Packard & Berger (2021), *Journal of Consumer Research*: across five studies including 1,000+ real customer interactions, concrete language increased satisfaction, purchase intent, and actual purchases; mechanism: customers infer the concrete speaker is *listening*. Reported magnitudes: ~5.6% more concreteness → ~8.9% higher satisfaction; ~30% higher spend in an email context. ✔ Packard, Moore & McFerran (2018): "I" pronouns from service employees outperform "we."
**Feeds:** the Specific rule; the reply move of echoing the reader's own concrete nouns.

## 3. Narrative — stories lower counterarguing

✔ Green & Brock (2000), *JPSP*: transportation into a narrative reduces counterarguing and resistance to persuasion. ✔ Braddock & Dillard (2016), *Communication Monographs*, meta-analysis: narratives reliably influence beliefs, attitudes, intentions, and behaviors; ✔ van Laer et al. (2014) meta on transportation. Arguments invite rebuttal; a story suspends it.
**Feeds:** persuasion.md's "argue it, or tell it" move. Guardrail: the Truth rule still governs — only real stories.

## 4. The screen distorts tone — and writers can't feel it

✔ Kruger, Epley, Parker & Ng (2005), *JPSP*: across five experiments, people overestimated their ability to convey sarcasm, humor, and tone by email — and to interpret others' — driven by egocentrism. Debias that worked: reading one's message aloud in the *opposite* tone eliminated the overconfidence. ✔ Byron (2008), *Academy of Management Review*: emotion in email is systematically miscommunicated; receivers skew negative.
**Feeds:** influence.md's misread-tone law and the hostile-reading test.

## 5. Receptiveness — the language of productive disagreement

✔ Yeomans, Minson, Collins, Chen & Gino (2020), *OBHDP*: an interpretable algorithm identified the linguistic profile of receptiveness (explicit acknowledgment of the opposing view, measured hedging, positive rather than negated framing); writers following the "receptiveness recipe" were judged more persuasive and more desirable future collaborators, and receptiveness early in a conversation forestalled later conflict escalation. ✔ Hussein & Tormala (2021): receptive arguments are more persuasive. ✔ Minson et al. (2024): receptiveness transmits — one party's receptive language increases the counterpart's.
✔ Related tension: Jeong, Minson, Yeomans & Gino (2019), *Management Science*: communicating warmth in distributive negotiations produced *worse* outcomes — friendliness isn't free in one-shot value-claiming.
**Feeds:** influence.md's disagreement recipe and the warmth-vs-firmness rule.

## 6. Certainty and hedging — including a failed replication we keep on purpose

✔ Karmarkar & Tormala (2010), *JCR*, found experts became more persuasive expressing uncertainty (the "incongruity hypothesis"). **But** ✔ a 2024 registered replication (Løhre et al., *JESP*, N=1,018) failed to reproduce it, instead supporting the confidence heuristic: expressed certainty helps persuasion irrespective of expertise (d≈0.18–0.25).
**Feeds:** the refined hedging rule. What survives all the evidence: cut reflexive hedges (Pinker; the confidence heuristic); keep deliberate hedges where they're honest (real uncertainty) or receptive (disagreement — §5); never hedge the ask. This entry stays in the file as a worked example of why we verify before we encode.

## 7. Values framing — argue in the reader's morals, not yours

✔ Feinberg & Willer (2015 *PSPB*; 2019 *SPPC* review): people spontaneously build arguments from their *own* moral values, and those arguments underperform; reframing a position in the audience's values (e.g., purity-framed environmental appeals for conservatives) persuades across divides, with effects replicated over a decade across inequality, environment, same-sex marriage, and candidate support.
**Feeds:** persuasion.md's "their values, not yours" rule.

## 8. Emotion, questions, and other supported-but-lighter findings

◇ Rocklage, Rucker & Nordgren (2018), *Psych Science*: the mere intent to persuade automatically makes language more emotional; emotionality helps hedonic contexts and can backfire with analytically-minded evaluation. Feeds the emotion-dial line. ◇ Huang, Yeomans et al. (2017), *JPSP*: question-asking — especially follow-ups — increases liking. Feeds coaching.md. ◇ Packard & Berger (2020), *Psych Science*: second-person "you" correlates with cultural success of texts; ◇ Berger (2023), *JCR*: present tense reads as more persuasive. Feed formats.md's post guidance.

## 9. The AI-era findings (instruction voice and mechanics)

✔ Politeness effects on model output are unstable across studies and models — impolite prompts hurt in 2024 cross-lingual work but *outperformed* polite ones on GPT-4o in 2025 — so tone is treated as flavor, not quality. ✔ Mechanical corruption is the reliable degrader: character-level typo attacks cost ~20%+ task performance in benchmark studies, and typos measurably hurt even frontier and reasoning models. ✔ Burstiness (sentence-length variance) is among the clearest measurable separators of human from machine prose.
**Feeds:** the rhythm rules, the instructions-vs-material guardrail, and the skill's own mechanically-impeccable house voice. Full experimental protocol: `tests/experiments/instruction-voice/` (lives in the repo, not shipped inside the skill).

## Reading this file honestly

These are averages from studies, mostly lab and field contexts that are not your exact context. Effects are directional tendencies, not laws; several classics in this literature have shrunk or died under replication (see §6), which is why entries carry status marks and why the eval harness — your writing, judged blind — outranks any citation here. When a finding and your tested results disagree, trust the test.
