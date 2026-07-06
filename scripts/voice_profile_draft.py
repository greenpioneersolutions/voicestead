#!/usr/bin/env python3
"""Draft a voice profile by measuring 2-3 writing samples. Keyless and deterministic.

Counts what a counter can count -- sentence rhythm, paragraph shape, contraction
habit, punctuation density, hedges, sentence openers, favorite words, question
rate -- and prints a draft ``voice-profile.md`` to stdout. Every number in the
output is computed from the samples; nothing is estimated. The draft mirrors the
sections of ``skills/voicestead/examples/voice-profile.example.md`` so the
3-minute interview can refine it instead of starting from a blank page.

The judgment calls stay open on purpose: the "Sounds like" adjectives and the
"Never says" list belong to the writer and the interview, not to a script.

Output goes to stdout by default; ``--out`` writes a file anywhere EXCEPT under
this repo's ``skills/`` tree. Profiles are personal-by-design (see .gitignore)
and this script never writes into the shippable tree.

The sentence splitter is shared with the test harness (tests/checks/
text_metrics.py) so the numbers here agree with the numbers CI checks. One
consequence to know: a line break counts as a sentence boundary, so pass
samples with natural wrapping (an email body, a chat message), not hard-wrapped
text.

Usage::

    python3 scripts/voice_profile_draft.py sample1.txt sample2.txt [sample3.txt]
    cat sample1.txt | python3 scripts/voice_profile_draft.py - sample2.txt
    python3 scripts/voice_profile_draft.py sample1.txt sample2.txt --out draft.md

Run from a full clone of the repository.
"""
import argparse
import os
import re
import statistics
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tests", "checks"))
try:
    import text_metrics as tm
except ImportError:
    print("voice_profile_draft: cannot import tests/checks/text_metrics.py -- "
          "run from a full clone of the repository.", file=sys.stderr)
    sys.exit(1)

# Curated contractions, so possessives ("Sam's") never count. Pronoun+'s entries
# (it's, that's, there's...) are near-always contractions in real prose.
CONTRACTIONS = frozenset("""
ain't aren't can't couldn't didn't doesn't don't hadn't hasn't haven't he'd
he'll he's here's how's i'd i'll i'm i've isn't it'd it'll it's let's mightn't
mustn't shan't she'd she'll she's shouldn't that'd that'll that's there'd
there'll there's they'd they'll they're they've wasn't we'd we'll we're we've
weren't what'll what're what's what've when's where'd where's who'd who'll
who're who's who've why's won't wouldn't y'all you'd you'll you're you've
""".split())

# Spelled-out counterparts: places the writer HAD the choice and spelled it out.
EXPANDED_FORMS = [
    "are not", "cannot", "can not", "could not", "did not", "does not",
    "do not", "had not", "has not", "have not", "i am", "i have", "i will",
    "i would", "is not", "it is", "let us", "should not", "that is",
    "there is", "they are", "was not", "we are", "we have", "we will",
    "were not", "will not", "would not", "you are",
]

# Hedge lexicon. "might" is included; bare "may" is not (the month, permission).
HEDGES = [
    "a bit", "a little", "apparently", "arguably", "i believe", "i guess",
    "i suppose", "i think", "in my opinion", "it appears", "it seems",
    "kind of", "maybe", "might", "perhaps", "possibly", "presumably",
    "probably", "seemingly", "somewhat", "sort of",
]

# Transition words worth reporting when they open sentences repeatedly.
TRANSITIONS = frozenset([
    "actually", "also", "and", "anyway", "basically", "but", "honestly",
    "however", "instead", "look", "meanwhile", "plus", "so", "still", "then",
    "though",
])

# Small function-word baseline; "favorite words" are what's left after these.
STOPWORDS = frozenset("""
a about after again all almost also am an and any are as at back be because
been before being between both but by can could day did do does down each even
first for from get go had has have he her here him his how i if in into is it
its just know like little me more most much my new no not now of off on one
only or other our out over own re s said same see she should so some still
such t than that the their them then there these they thing think this those
through time to too two under up us very was way we well were what when where
which while who why will with would you your
""".split())


def _lower(text):
    return tm._normalize(text).lower()


def _tokens(text):
    """Lowercased word tokens with edge apostrophes stripped ("'word'" -> "word")."""
    return [t.strip("'") for t in re.findall(r"[a-z0-9']+", _lower(text))]


def _count_phrases(low, phrases):
    """Occurrences of each phrase (word-boundary match) in lowercased text."""
    found = {}
    for p in phrases:
        n = len(re.findall(r"\b" + re.escape(p) + r"\b", low))
        if n:
            found[p] = n
    return found


def _rate(count, words, per):
    return count / max(words, 1) * per


def sentence_stats(sentences):
    lens = [tm.word_count(s) for s in sentences]
    lens = [n for n in lens if n > 0]
    if not lens:
        return {"count": 0, "mean": 0.0, "sd": 0.0, "min": 0, "max": 0}
    return {
        "count": len(lens),
        "mean": statistics.mean(lens),
        "sd": statistics.pstdev(lens),
        "min": min(lens),
        "max": max(lens),
    }


def paragraph_stats(samples):
    """Sentences-per-paragraph over blank-line-separated paragraphs, per sample."""
    per_para = []
    for sample in samples:
        for para in re.split(r"\n\s*\n", tm._normalize(sample).strip()):
            n = len(tm.split_sentences(para))
            if n:
                per_para.append(n)
    if not per_para:
        return {"count": 0, "mean_sentences": 0.0, "single_pct": 0.0, "max_sentences": 0}
    singles = sum(1 for n in per_para if n == 1)
    return {
        "count": len(per_para),
        "mean_sentences": statistics.mean(per_para),
        "single_pct": singles / len(per_para) * 100,
        "max_sentences": max(per_para),
    }


def contraction_stats(text, total_words):
    hits = [t for t in _tokens(text) if t in CONTRACTIONS]
    expanded = sum(_count_phrases(_lower(text), EXPANDED_FORMS).values())
    choices = len(hits) + expanded
    return {
        "count": len(hits),
        "per_100": _rate(len(hits), total_words, 100),
        "expanded": expanded,
        "preference_pct": (len(hits) / choices * 100) if choices else None,
    }


def punctuation_stats(text, total_words):
    norm = tm._normalize(text)
    em = norm.count("—") + len(re.findall(r"(?<!-)--(?!-)", norm))
    return {
        "em_dash_per_1000": _rate(em, total_words, 1000),
        "semicolon_per_1000": _rate(norm.count(";"), total_words, 1000),
        "paren_per_1000": _rate(norm.count("("), total_words, 1000),
    }


def hedge_stats(text, total_words):
    found = _count_phrases(_lower(text), HEDGES)
    total = sum(found.values())
    top = sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    return {"count": total, "per_1000": _rate(total, total_words, 1000), "top": top}


def opener_stats(sentences):
    """First word of each sentence; repeats of 3+ are a habit worth naming."""
    firsts = []
    for s in sentences:
        m = re.match(r"[A-Za-z0-9']+", s)
        if m:
            firsts.append(m.group(0).lower().strip("'"))
    if not firsts:
        return {"total": 0, "distinct_pct": 0.0, "repeated": [], "transitions": []}
    counts = {}
    for w in firsts:
        counts[w] = counts.get(w, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "total": len(firsts),
        "distinct_pct": len(counts) / len(firsts) * 100,
        "repeated": [(w, n) for w, n in ordered if n >= 3],
        "transitions": [(w, n) for w, n in ordered if w in TRANSITIONS and n >= 2],
    }


def lexical_favorites(text, min_count=3, top=8):
    """Non-stopword words used min_count+ times, most-used first (ties alphabetical)."""
    counts = {}
    for t in _tokens(text):
        if len(t) < 3 or t in STOPWORDS or t in CONTRACTIONS or t.isdigit():
            continue
        counts[t] = counts.get(t, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(w, n) for w, n in ordered if n >= min_count][:top]


def question_pct(sentences):
    if not sentences:
        return 0.0
    q = sum(1 for s in sentences if s.rstrip("\"')]").endswith("?"))
    return q / len(sentences) * 100


def representative_lines(samples):
    """One verbatim line per sample: the sentence closest to that sample's own mean
    length (ties go to the earlier sentence). Deterministic, never invented."""
    lines = []
    for sample in samples:
        sents = tm.split_sentences(sample)
        pairs = [(s, tm.word_count(s)) for s in sents if tm.word_count(s) > 0]
        if not pairs:
            continue
        mean = statistics.mean(n for _, n in pairs)
        best = min(range(len(pairs)), key=lambda i: (abs(pairs[i][1] - mean), i))
        lines.append(pairs[best][0])
    return lines


def analyze(samples):
    """Compute every metric from the samples. Returns raw (unrounded) numbers;
    render() does the formatting."""
    full = "\n\n".join(samples)
    sentences = tm.split_sentences(full)
    words = tm.word_count(full)
    return {
        "samples": len(samples),
        "words": words,
        "sentence_len": sentence_stats(sentences),
        "paragraphs": paragraph_stats(samples),
        "contractions": contraction_stats(full, words),
        "punct": punctuation_stats(full, words),
        "hedges": hedge_stats(full, words),
        "openers": opener_stats(sentences),
        "favorites": lexical_favorites(full),
        "question_pct": question_pct(sentences),
        "sample_lines": representative_lines(samples),
    }


def render(m):
    """Render the metrics dict as a draft voice-profile.md (markdown string)."""
    sl, pg, ct = m["sentence_len"], m["paragraphs"], m["contractions"]
    pu, hg, op = m["punct"], m["hedges"], m["openers"]

    def f1(x):
        return "%.1f" % x

    def pct(x):
        return "%d%%" % int(round(x))

    def pairs(items):
        return ", ".join('"%s" (x%d)' % (w, n) for w, n in items)

    L = ["# Voice Profile — draft (measured from %d samples, %d words)"
         % (m["samples"], m["words"]), ""]
    L += ["_Every number here was computed by scripts/voice_profile_draft.py from the",
          "samples you provided; nothing is estimated. This is a draft — the 3-minute",
          "interview turns it into a profile you've confirmed. Correct anything that",
          "reads wrong; your correction outranks the count._", ""]

    L.append("Sounds like: the interview fills this in. Adjectives are a judgment call,")
    L.append("and a script that guessed them would be inventing. Measured signals to")
    L.append("react to:")
    L.append("- Sentences average %s words (sd %s, range %d–%d) across %d sentences."
             % (f1(sl["mean"]), f1(sl["sd"]), sl["min"], sl["max"], sl["count"]))
    L.append("- Paragraphs average %s sentences; %s are a single sentence; the longest runs %d."
             % (f1(pg["mean_sentences"]), pct(pg["single_pct"]), pg["max_sentences"]))
    if ct["count"] or ct["expanded"]:
        line = ("- Contractions: %d in %d words (%s per 100)."
                % (ct["count"], m["words"], f1(ct["per_100"])))
        if ct["preference_pct"] is not None:
            line += " Given the choice, you contract %s of the time." % pct(ct["preference_pct"])
        L.append(line)
    else:
        L.append("- No contractions and no spelled-out forms found — too little signal to call.")
    if m["question_pct"]:
        L.append("- Questions end %s of sentences." % pct(m["question_pct"]))
    else:
        L.append("- No sentence ends in a question mark.")
    L.append("")

    L.append("Signature moves (measured):")
    L.append("- Per 1,000 words: em-dashes %s, semicolons %s, parentheticals %s."
             % (f1(pu["em_dash_per_1000"]), f1(pu["semicolon_per_1000"]),
                f1(pu["paren_per_1000"])))
    if hg["count"]:
        L.append("- Hedges: %s per 1,000 words. Most used: %s."
                 % (f1(hg["per_1000"]), pairs(hg["top"])))
    else:
        L.append("- No hedges from the measured list (maybe, probably, i think, ...).")
    if op["repeated"]:
        L.append("- Repeated sentence-starts: %s." % pairs(op["repeated"]))
    else:
        L.append("- Sentence-starts vary: %s of sentences open with a distinct first word;"
                 " none repeats 3 times." % pct(op["distinct_pct"]))
    if op["transitions"]:
        L.append("- Sentence-opening transitions you favor: %s." % pairs(op["transitions"]))
    if m["favorites"]:
        L.append("- Words you reach for: %s." % pairs(m["favorites"]))
    else:
        L.append("- No favorite words yet: outside common words, nothing repeats 3 times or more.")
    L.append("")

    L.append("Never says: the script can count what you do, never what you avoid. In the")
    L.append("interview, list the words a model would reach for that you never would.")
    L.append("")
    L.append("Registers (if voice shifts by medium): the samples were measured as one pool.")
    L.append("If they came from different media (Slack, email, a post), note here what")
    L.append("changes between them.")
    L.append("")
    L.append("Sample lines (verbatim; per sample, the sentence closest to that sample's")
    L.append("average sentence length):")
    for i, line in enumerate(m["sample_lines"], 1):
        L.append('%d. "%s"' % (i, line))
    L.append("")
    return "\n".join(L)


def read_samples(paths):
    """Read each path ('-' reads stdin, at most once) as one sample; exit 1 on bad input."""
    if len(paths) < 2:
        print("voice_profile_draft: need at least 2 samples (got %d). Pass 2-3 "
              "pieces you actually wrote -- files, or '-' to read one from stdin."
              % len(paths), file=sys.stderr)
        sys.exit(1)
    if paths.count("-") > 1:
        print("voice_profile_draft: '-' (stdin) can supply at most one sample.",
              file=sys.stderr)
        sys.exit(1)
    if len(paths) > 3:
        print("voice_profile_draft: %d samples given; 2-3 is typical. Using all of them."
              % len(paths), file=sys.stderr)
    samples = []
    for p in paths:
        if p == "-":
            text = sys.stdin.read()
        else:
            if not os.path.isfile(p):
                print("voice_profile_draft: no such file: %s" % p, file=sys.stderr)
                sys.exit(1)
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
        if not text.strip():
            print("voice_profile_draft: sample is empty: %s" % p, file=sys.stderr)
            sys.exit(1)
        samples.append(text)
    return samples


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Measure 2-3 writing samples into a draft voice-profile.md "
                    "(stdout by default).")
    ap.add_argument("samples", nargs="*",
                    help="sample files; '-' reads one sample from stdin")
    ap.add_argument("--out", default=None,
                    help="write the draft to this path instead of stdout "
                         "(anywhere except the skills/ tree)")
    args = ap.parse_args(argv)

    draft = render(analyze(read_samples(args.samples)))

    if args.out:
        dest = os.path.abspath(args.out)
        if dest.startswith(os.path.join(REPO, "skills") + os.sep):
            print("voice_profile_draft: refusing to write %s -- profiles are "
                  "personal-by-design and never go into the shippable skills/ tree. "
                  "Pick another path (or redirect stdout) and place the file yourself."
                  % args.out, file=sys.stderr)
            return 1
        out_dir = os.path.dirname(dest)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(draft)
        print("wrote %s" % dest, file=sys.stderr)
    else:
        sys.stdout.write(draft)
    return 0


if __name__ == "__main__":
    sys.exit(main())
