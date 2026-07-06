# Instruction-Voice Judge Rubric

You grade one piece of writing produced from an instruction. You see: the CLEAN task (facts + constraints + intended reader register) and the OUTPUT. You do NOT see the instruction wrapper's voice — judge only the output against the clean task. Score 1–5, discerning, lower when torn.

Return ONLY JSON:
```json
{"scores": {
  "task_quality": {"score": 3, "why": "one sentence"},
  "instruction_adherence": {"score": 3, "why": "one sentence"},
  "tone_fidelity": {"score": 3, "why": "one sentence"},
  "register_contamination": {"score": 3, "why": "one sentence"},
  "human_rhythm": {"score": 3, "why": "one sentence"}},
 "would_send": true}
```

- **task_quality** — 1: fails the job; 3: competent; 5: a thoughtful professional would send it as-is.
- **instruction_adherence** — against the clean constraint list. 1: multiple constraints broken; 3: one broken; 5: all satisfied exactly.
- **tone_fidelity** — does the OUTPUT's tone serve the stated reader/register? 1: wrong room entirely (e.g., hostile note to a boss); 3: serviceable but off; 5: precisely the room.
- **register_contamination** — evidence a *different* voice leaked into the output (insults, ornate vocabulary, hype, baby-talk) that the stated reader wouldn't expect. 5 = no leakage; 1 = the output visibly wears someone else's voice. If facts appear misspelled or numbers look mutated, note it in "why".
- **human_rhythm** — 1: metronomic/mechanical; 5: varied, alive, reads aloud naturally.
