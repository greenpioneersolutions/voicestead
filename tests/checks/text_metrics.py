"""Deterministic text checks for Voicestead outputs.

Pure stdlib. No network. Each check returns a dict:
    {"id": str, "severity": "hard"|"soft", "passed": bool, "detail": str, "metric": <optional number>}

The philosophy (see tests/TESTING.md): code checks verify *form*, never *substance*.
'hard' checks are gates the skill must never fail. 'soft' checks are signals that feed
the score and hand candidates to the LLM judge — a single soft flag is not a failure.

Unicode: run() and every public check_* function pass text through _normalize() first,
so curly apostrophes and quotes cannot slip past ascii patterns. Em/en dashes are left
alone on purpose — the dash is a legitimate style element, not slop.

run() raises ValueError for an unknown check id. A typo in a case file must fail loudly,
never report green.
"""
import re
import statistics
from typing import Dict, List, Tuple

# ---- unicode punctuation -> ascii (dashes deliberately untouched) ----
_PUNCT_MAP = {
    "’": "'",   # right single quotation mark
    "‘": "'",   # left single quotation mark
    "“": '"',   # left double quotation mark
    "”": '"',   # right double quotation mark
}


def _normalize(text: str) -> str:
    """Map unicode punctuation to ascii BEFORE any pattern matching."""
    for k, v in _PUNCT_MAP.items():
        text = text.replace(k, v)
    return text


# ---- High-confidence slop phrases: almost never justified in real writing ----
# Apostrophes are optional ('?) so both curly-normalized AND apostrophe-less
# variants ("todays") are caught. "at the end of the day" requires the trailing
# comma (discourse-marker form) so the literal deadline sense stays legal;
# "in conclusion" accepts ',' or ':'.
HIGH_CONF_TELLS = [
    r"in today'?s (?:rapidly )?(?:evolving|changing|fast-paced) (?:landscape|world|environment)",
    r"it'?s worth noting that",
    r"at the end of the day,",
    r"that being said",
    r"needless to say",
    r"in conclusion[,:]",
    r"when it comes to",
    r"navigate the complexities of",
    r"unlock (?:the|your) (?:full )?potential",
    r"in the realm of",
]

# ---- Category tell-words (soft): mirror references/tells.md. Context decides. ----
# Base forms only; check_tell_flags matches inflections (delve -> delves/delved/delving,
# seamless -> seamlessly, synergy -> synergies) via _inflect().
TELL_WORDS = [
    "delve", "leverage", "seamless", "robust", "pivotal", "elevate", "foster",
    "harness", "utilize", "facilitate", "tapestry", "realm", "holistic",
    "transformative", "cutting-edge", "myriad", "plethora", "underscore",
    "bolster", "streamline", "paradigm", "synergy", "commendable", "meticulous",
]


def _inflect(w: str) -> str:
    """Regex fragment matching a base tell-word plus its common inflections."""
    if w.endswith("e"):
        return re.escape(w[:-1]) + r"(?:e|es|ed|ing)"
    if w.endswith("y"):
        return re.escape(w[:-1]) + r"(?:y|ies)"
    return re.escape(w) + r"(?:s|es|ed|ing|ly)?"


THROATCLEAR_OPENERS = [
    r"^\s*(?:hey|hi|hello)?[,\s]*i just wanted to",
    r"^\s*i just wanted to",
    r"^\s*i (?:hope|trust) (?:this|you)",
    r"^\s*in this (?:response|email|message|document)",
    r"^\s*just (?:reaching out|checking in|wanted to)",
    r"^\s*i'?m writing to",
    r"^\s*first(?:ly)?,? i(?:'?d| would) like to",
]

# ---- Formula structures (soft) ----
FORMULA_PATTERNS = [
    (r"\bit'?s not (?:just )?[^.,;]{1,40}?,? it'?s\b", "false-contrast (it's not X, it's Y)"),
    (r"\bthe question is(?:n'?t| not)\b[^.?]{1,60}?,? it'?s\b", "false-contrast (the question isn't X)"),
    (r"\bwhat if i told you\b", "rhetorical setup"),
    (r"\bthink about it:", "rhetorical setup"),
    (r"\bhere'?s the thing\b", "throat-clearing frame"),
    (r"\band that'?s (?:okay|ok)\.", "canned reassurance"),
]

# ---- Onboarding re-pitch (soft): once a profile exists, never nag the setup/interview offer ----
ONBOARDING_PITCH = [
    r"\d+[-\s]?minute voice setup",
    r"\bvoice setup\b",
    r"\binfluence interview\b",
    r"want to (?:do|run|set up|try)[^.?!]{0,40}(?:voice|influence)",
    r"build (?:you )?a voice profile",
]

# When the PROMPT itself asks for setup, pitch language in the reply is responsive, not a nag.
_ONBOARDING_REQUEST = re.compile(
    r"voice (?:setup|profile)|influence interview|interview me|writers who shaped", re.I)

# ---- False agency (soft): inanimate subjects doing human things ----
# Deliberately narrow families for precision; the judge catches the long tail.
FALSE_AGENCY = [
    r"\b(?:the|this|our|these)\s+data\s+"
    r"(?:tells?|says?|speaks?|thinks?|wants?|knows?|shows?\s+us|suggests?\s+(?:that\s+)?we)\b",
    r"\b(?:the|these|our)\s+numbers\s+"
    r"(?:shows?|says?|tells?|speaks?|wants?|argues?|suggests?\s+we)\b",
    r"\b(?:the|these|our)\s+(?:metrics|figures|results)\s+"
    r"(?:tells?\s+us|says?\b|speaks?\b|wants?\b|argues?\b)",
    r"\b(?:the|this|our)\s+(?:document|report|memo|deck|analysis|study|proposal)\s+"
    r"(?:outlines?|argues?|believes?|thinks?|wants?|insists?|asks?\s+us|tells?\s+(?:us|you)|says?\s+(?:that|we|you)\b)",
    r"\b(?:the|this|our)\s+(?:decision|conversation|culture|market|process|strategy)\s+"
    r"(?:emerged|evolved|decided|chose|wants?|rewards?|demands?|moved\s+toward)\b",
]

# ---- Zombie nouns (soft): nominalization suffixes; stem must be 4+ chars so
# "city"/"unity"/"vision" don't count. ----
_NOMINAL = re.compile(r"\b[a-z]{4,}(?:tion|sion|ment|ance|ence|ity)s?\b")

_SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]?\s+(?=[A-Za-z0-9])")
_ABBREV = re.compile(r"\b(?:e\.g|i\.e|etc|vs|Mr|Mrs|Ms|Dr|Inc|Ltd|Jr|Sr|a\.m|p\.m|U\.S)\.$", re.I)
_BULLET = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#{1,6}\s+)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_EMPHASIS = re.compile(r"[*_]{1,3}")
_URL = re.compile(r"https?://\S+")

# Quoted spans are citation, not the writer's own prose. The single-quote form is
# guarded by non-word boundaries so apostrophes ("don't ... it's") never pair up.
_DQUOTE_SPAN = re.compile(r'"[^"]{0,300}"')
_SQUOTE_SPAN = re.compile(r"(?<!\w)'[^']{0,300}'(?!\w)")


def _strip_quoted(text: str) -> str:
    text = _DQUOTE_SPAN.sub(" ", text)
    text = _SQUOTE_SPAN.sub(" ", text)
    return text


def split_sentences(text: str) -> List[str]:
    """Line-aware sentence splitter. Markdown markers (bullets, headers, bold, link
    targets) are stripped, newlines are sentence boundaries, numbered-list markers
    ('1.') never become one-word sentences, and common abbreviations don't split."""
    text = _normalize(text)
    out: List[str] = []
    for line in re.split(r"\n+", text.strip()):
        line = _BULLET.sub("", line)
        line = _MD_LINK.sub(r"\1", line)
        line = _EMPHASIS.sub("", line).strip()
        if not line:
            continue
        rough = _SENT_SPLIT.split(re.sub(r"\s+", " ", line))
        start = len(out)
        for s in rough:
            if len(out) > start and re.fullmatch(r"\d+[.)]", out[-1].strip()):
                out[-1] = s          # '1.' was a list marker, not a sentence
            elif len(out) > start and _ABBREV.search(out[-1]):
                out[-1] = out[-1] + " " + s
            else:
                out.append(s)
    return [s.strip() for s in out if s.strip()]


_H2_LINE = re.compile(r"^## +(\S.*?)\s*$")
# A fence line per CommonMark: a run of 3+ backticks or tildes indented at most
# three spaces (four or more is an indented code block, not a fence). group(1) is
# the run; group(2) is the rest of the line — an info string is legal on an opener
# but a closer must be bare.
_FENCE_LINE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def split_sections(text: str) -> List[Tuple[str, str]]:
    """Split a markdown document on H2 headings ('## ' at line start) into
    (heading, body) pairs, in document order. Fence-aware where split_sentences
    never needed to be: a '## ' line inside a ``` or ~~~ fenced block is content,
    not a boundary. Fences pair the CommonMark way: a fence closes only on a bare
    run of the SAME character at least as LONG as its opener, so ~~~ lines inside
    a ``` block, or a ``` example inside a ```` block, stay content; an indented
    (4+ spaces) run of backticks is code-block content and never opens a fence.
    Text before the first H2 becomes a ("", preamble) section; a document with no
    H2 headings comes back as one ("", text) section, so per-section callers grade
    it exactly like the whole document. H3+ headings and '##nospace' lines never
    split."""
    sections: List[Tuple[str, str]] = []
    heading, buf = "", []
    fence = None  # (fence char, opening run length) while inside a fence, else None
    for line in text.splitlines():
        f = _FENCE_LINE.match(line)
        if f:
            run, rest = f.group(1), f.group(2)
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not rest.strip():
                fence = None
            buf.append(line)
            continue
        m = None if fence else _H2_LINE.match(line)
        if m:
            body = "\n".join(buf).strip()
            if heading or body:
                sections.append((heading, body))
            heading, buf = m.group(1), []
        else:
            buf.append(line)
    body = "\n".join(buf).strip()
    if heading or body or not sections:
        sections.append((heading, body))
    return sections


def _words(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", s)


def word_count(text: str) -> int:
    """Word count over normalized text; markdown link targets and bare URLs don't count."""
    text = _normalize(text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = _URL.sub(" ", text)
    return len(_words(text))


# ---- spelled-number licensing (prompt/source side only) ----
_WORD_NUMS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}


def _spelled_numbers(t: str) -> set:
    """Digit strings licensed by spelled numbers zero..ninety-nine ("fourteen" -> "14",
    "seventy-three" -> "73"). The pair word is a lookahead, not consumed, so 'exactly
    two big outages' still licenses 2."""
    out = set()
    for m in re.finditer(r"\b([a-z]+)(?=[-\s]+([a-z]+)\b)?", t.lower()):
        a, b = m.group(1), m.group(2)
        if a in _WORD_NUMS:
            v = _WORD_NUMS[a]
            if b in _WORD_NUMS and v >= 20 and v % 10 == 0 and _WORD_NUMS[b] < 10:
                v += _WORD_NUMS[b]
            out.add(str(v))
    return out


# ---- shared licensing helper (Truth gate v2) ----
_QUOTE_MIN_WORDS = 5


def _squash(t: str) -> str:
    """Lowercase + collapse whitespace after _normalize: the comparison space for
    substring licensing (quotes, citations, URLs)."""
    return re.sub(r"\s+", " ", _normalize(t)).strip().lower()


# --------------------------- checks ---------------------------

def check_no_invented_numbers(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
    """HARD (Truth): any figure in the output must appear in the prompt OR the source.

    Rules:
    - the $/% tag stays on the token when testing exemption, so '9%', '$8', '$9M'
      and '9.5' are figures and must be sourced; only BARE single-digit integers
      (counts/ordinals like "3 options") are exempt;
    - markdown links are unwrapped before extraction (link text can hide figures);
    - bracketed placeholders ([X], [amount], [date]) are allowed;
    - spelled numbers zero..ninety-nine in the prompt/source license their digit
      forms ("fourteen incidents" licenses 14).

    Honest residual limits (judge-tier concerns, not covered here):
    - spelled-out fabrications in the OUTPUT ("seventy-three percent") pass — a
      deterministic word-number detector on the output side risks idiom FPs;
    - a bare small int with a magnitude word ("9 million", "5x") is still exempt;
    - years get no special handling: unsourced "2026" is flagged like any figure.
    """
    def toks(t):
        t = _normalize(t)
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)   # unwrap md links, keep the text
        t = re.sub(r"\[[^\]]*\]", " ", t)                # then drop [placeholders]
        return re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", t)

    def bare(r):
        return r.replace("$", "").replace(",", "").rstrip("%")

    in_bare = {bare(r) for r in toks(prompt)} | {bare(r) for r in toks(source)}
    in_bare |= _spelled_numbers(_normalize(prompt)) | _spelled_numbers(_normalize(source))
    invented = set()
    for r in toks(output):
        b = bare(r)
        if b in in_bare:
            continue
        exempt = b.isdigit() and int(b) <= 9 and "$" not in r and "%" not in r and "." not in b
        if not exempt:
            invented.add(b)
    passed = len(invented) == 0
    detail = "no unsourced figures" if passed else f"figures not in input (possible fabrication): {sorted(invented)}"
    return {"id": "no_invented_numbers", "severity": "hard", "passed": passed, "detail": detail}


def check_no_invented_quotes(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
    """HARD (Truth): every quotation in the output must appear in the prompt OR source.

    A quotation is a quoted span of >= _QUOTE_MIN_WORDS words — double or single
    quotes, curly variants normalized first. Licensing is a whitespace/case-normalized
    substring match against prompt+source; a trailing period or comma inside the
    closing quote mark is ignored (American-style punctuation placement must not read
    as fabrication). Spans under the word floor are exempt: scare quotes and quoted
    terms are emphasis, not citation.

    Honest residual limits (judge-tier concerns, not covered here):
    - PARAPHRASED fabrication ('the auditor said the pipeline was the cleanest ever')
      has no quote marks and passes — the judge's truth dimension owns it;
    - a real, licensed quote ATTRIBUTED to the wrong speaker passes;
    - spans over 300 chars exceed _DQUOTE_SPAN/_SQUOTE_SPAN and are not extracted;
    - a fabricated quote of 4 words or fewer rides the scare-quote exemption.
    """
    text = re.sub(r"\s+", " ", _normalize(output))
    spans = [m.group(0)[1:-1] for m in _DQUOTE_SPAN.finditer(text)]
    spans += [m.group(0)[1:-1] for m in _SQUOTE_SPAN.finditer(text)]
    licensed = _squash(prompt) + "\n" + _squash(source)
    invented = []
    for span in spans:
        if len(_words(span)) < _QUOTE_MIN_WORDS:
            continue
        squashed = _squash(span)
        if squashed in licensed or squashed.rstrip(".,;:!?") in licensed:
            continue
        invented.append(span if len(span) <= 60 else span[:57] + "...")
    passed = len(invented) == 0
    detail = "no unsourced quotations" if passed else f"quotations not in input (possible fabrication): {invented}"
    return {"id": "no_invented_quotes", "severity": "hard", "passed": passed, "detail": detail}


# ---- citation-shaped patterns (Truth gate v2). Narrow families for precision —
# the judge owns paraphrased or novel shapes. ----
_CIT_AUTHOR_YEAR = re.compile(
    r"\b([A-Z][A-Za-z'-]+)(?:\s+(?:et al\.?|&\s+[A-Z][A-Za-z'-]+|and\s+[A-Z][A-Za-z'-]+))?,?\s*\((\d{4})\)")
_CIT_BRACKET_REF = re.compile(r"\[(\d{1,3})\](?!\()")
_CIT_DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+")
_CIT_ACCORDING_TO = re.compile(r"\b[Aa]ccording to (?:the )?([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,3})")
_CIT_YEAR_STUDY = re.compile(r"\ba (\d{4}) (?:study|survey|report|paper|meta-analysis)\b", re.I)

# Capitalized filler words carry no licensing weight for 'according to' entities:
# 'the'/'a' appear in virtually every prompt, so letting them license would wave
# through the most common borrowed-authority shapes ('According to The Lancet',
# 'According to A Harvard Study', 'According to New York Magazine').
_CIT_ENTITY_STOPWORDS = {"the", "a", "an", "of", "and", "new"}


def _name_licensed(name: str, lic_words: set) -> bool:
    """A cited surname is licensed when every _words() token of it appears in the
    input. _words() splits at hyphens, so 'Smith-Jones' checks 'smith' AND 'jones'
    against the same tokenization the licensing set was built with (apostrophe
    names like O'Brien stay one token either way)."""
    parts = _words(name)
    return bool(parts) and all(p.lower() in lic_words for p in parts)


def check_no_invented_citations(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
    """HARD (Truth): citation-shaped claims in the output must be licensed by the input.

    Families, each with its own licensing rule (prompt OR source):
    - Author (Year) — 'Alvarez (2021)', 'Kim et al. (2020)': the surname AND the year
      must both appear in the input; a hyphenated surname ('Smith-Jones') is licensed
      part-by-part, matching how the input side is tokenized;
    - bracketed refs — '[1]': the same '[n]' must appear in the input (markdown links
      '[text](url)' are exempt via the (?!\\() guard);
    - DOIs — '10.xxxx/...': the same DOI string must appear in the input;
    - attribution — 'according to <ProperNoun...>': some non-stopword word of the named
      entity must appear in the input. Capitalized fillers (The/A/An/Of/And/New) never
      license — 'the' is in every prompt, and 'According to The Lancet' must not ride
      on it. 'according to the plan' has no proper noun and is exempt, as is an entity
      made only of stopwords;
    - vague-study — 'a 2019 study/survey/report/paper/meta-analysis': the year must
      appear in the input.

    Honest residual limits (judge-tier concerns, not covered here):
    - shapeless authority ('studies show', 'experts agree') has no pattern to match;
    - year-level licensing can't tell 'a 2019 study' from an input where 2019 was
      only a date;
    - a name present in the input can be misattributed ('according to Sarah' when
      Sarah said something else);
    - one licensed content word licenses a whole 'according to' entity — 'According
      to New York Magazine' still passes when the input merely mentions 'york';
    - APA-style 'Smith, 2019' without parentheses is not extracted.
    """
    text = re.sub(r"\s+", " ", _normalize(output))
    lic = _squash(prompt) + "\n" + _squash(source)
    lic_words = set(_words(lic))
    hits = []
    for m in _CIT_AUTHOR_YEAR.finditer(text):
        if not _name_licensed(m.group(1), lic_words) or m.group(2) not in lic_words:
            hits.append(m.group(0))
    for m in _CIT_BRACKET_REF.finditer(text):
        if "[" + m.group(1) + "]" not in lic:
            hits.append(m.group(0))
    for m in _CIT_DOI.finditer(text):
        if m.group(0).rstrip(".,;:)").lower() not in lic:
            hits.append(m.group(0))
    for m in _CIT_ACCORDING_TO.finditer(text):
        entity = [w for w in _words(m.group(1)) if w.lower() not in _CIT_ENTITY_STOPWORDS]
        if entity and not any(w.lower() in lic_words for w in entity):
            hits.append(m.group(0))
    for m in _CIT_YEAR_STUDY.finditer(text):
        if m.group(1) not in lic_words:
            hits.append(m.group(0))
    passed = len(hits) == 0
    detail = "no unsourced citations" if passed else f"citation-shaped claims not in input (possible fabrication): {hits}"
    return {"id": "no_invented_citations", "severity": "hard", "passed": passed, "detail": detail}


# ---- URL licensing (Truth gate v2). String-level only — never any network call. ----
_URL_ANY = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.I)


def check_no_invented_urls(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
    """HARD (Truth): every URL in the output must appear in the prompt OR the source.

    String-level substring match, case-insensitive, whitespace-collapsed — no network
    calls, ever (reachability is not the question; licensing is). Extraction covers
    bare http(s) URLs, markdown link targets, and scheme-less 'www.' links; trailing
    sentence punctuation is stripped before comparison. A link the user never supplied
    is a fabrication even when it points somewhere real — the skill's rule is a
    bracketed placeholder, not a remembered address.

    Honest residual limits (judge-tier concerns, not covered here):
    - bare domains with no scheme or 'www.' ('see example.com/docs') are not seen;
    - a URL containing ')' or ']' loses its tail to the markdown guard, so a
      fabricated tail behind that character escapes;
    - mailto: and other non-http schemes are not extracted.
    """
    text = re.sub(r"\s+", " ", _normalize(output))
    lic = _squash(prompt) + "\n" + _squash(source)
    invented = []
    for m in _URL_ANY.finditer(text):
        url = m.group(0).rstrip(".,;:!?").lower()
        if url and url not in lic:
            invented.append(url)
    passed = len(invented) == 0
    detail = "no unsourced urls" if passed else f"urls not in input (possible fabrication): {invented}"
    return {"id": "no_invented_urls", "severity": "hard", "passed": passed, "detail": detail}


def check_no_high_conf_tells(output: str, **kw) -> Dict:
    """HARD: high-confidence slop phrases. Whitespace is collapsed first (a tell split
    across a line break still counts) and quoted spans are dropped (quoting a tell in
    feedback — 'cut "in today's rapidly evolving landscape"' — is citation, not slop)."""
    text = re.sub(r"\s+", " ", _normalize(output))
    text = _strip_quoted(text)
    hits = []
    for pat in HIGH_CONF_TELLS:
        for m in re.finditer(pat, text, re.I):
            hits.append(m.group(0))
    passed = len(hits) == 0
    return {"id": "no_high_conf_tells", "severity": "hard", "passed": passed,
            "detail": "clean" if passed else f"high-confidence slop phrases: {hits}"}


def check_tell_flags(output: str, threshold_per_200: float = 2.0, **kw) -> Dict:
    """SOFT: count category tell-words, inflections included; the judge adjudicates context.
    The rate uses a 200-word floor — the same protection triads_ok and zombie_nouns give
    short texts — because per-section grading feeds this check individual sections: one
    contextual tell-word in a short note ('we became foster parents') stays the judge's
    call, while a cluster still crosses the threshold."""
    low = _normalize(output).lower()
    found = {}
    for w in TELL_WORDS:
        c = len(re.findall(r"\b" + _inflect(w) + r"\b", low))
        if c:
            found[w] = c
    total = sum(found.values())
    rate = total / max(word_count(output), 200) * 200
    passed = rate <= threshold_per_200
    return {"id": "tell_flags", "severity": "soft", "passed": passed, "metric": round(rate, 2),
            "detail": (f"{total} candidate tell-word(s) ({rate:.1f}/200w): {found}. Judge adjudicates context."
                       if found else "no category tell-words")}


def check_formula_structures(output: str, **kw) -> Dict:
    text = re.sub(r"\s+", " ", _normalize(output))
    hits = []
    for pat, label in FORMULA_PATTERNS:
        if re.search(pat, text, re.I):
            hits.append(label)
    passed = len(hits) == 0
    return {"id": "formula_structures", "severity": "soft", "passed": passed,
            "detail": "none" if passed else f"formula structures: {hits}"}


def check_burstiness(output: str, min_cv: float = 0.4, **kw) -> Dict:
    """SOFT: rhythm variance. CV = stddev/mean of sentence word-counts.
    Also flags 3+ consecutive sentences within +/-2 words (metronomic).
    split_sentences is line-aware, so bulleted/numbered slop is assessed, not skipped."""
    sents = split_sentences(output)
    lens = [word_count(s) for s in sents if word_count(s) > 0]
    if len(lens) < 3:
        return {"id": "burstiness_ok", "severity": "soft", "passed": True, "metric": None,
                "detail": "too short to assess rhythm"}
    mean = statistics.mean(lens)
    cv = (statistics.pstdev(lens) / mean) if mean else 0.0
    run_len = 1
    metronome = False
    for i in range(1, len(lens)):
        if abs(lens[i] - lens[i - 1]) <= 2:
            run_len += 1
            if run_len >= 3:
                metronome = True
        else:
            run_len = 1
    passed = cv >= min_cv and not metronome
    detail = f"CV={cv:.2f} (>= {min_cv} good); lens={lens}"
    if metronome:
        detail += "; 3+ consecutive near-equal sentences (metronomic)"
    return {"id": "burstiness_ok", "severity": "soft", "passed": passed, "metric": round(cv, 2), "detail": detail}


def check_triads(output: str, max_per_200: float = 1.0, **kw) -> Dict:
    """SOFT: the rule of three. Counts 'A, B(,) and/or C' — Oxford comma optional —
    per 200 words. Appositives ('Sam, who runs infra, and we...') and vertical
    markdown lists are not triads. The rate uses a 200-word floor, so one legitimate
    enumeration in a short email is reported but does not fail."""
    text = _normalize(output)
    clean = "\n".join(l for l in text.splitlines() if not _BULLET.match(l))
    pat = (r"\b[\w'-]+(?:\s+[\w'-]+){0,3},\s+(?!(?:who|which|whose|where|when|and|or)\b)"
           r"[\w'-]+(?:\s+[\w'-]+){0,3},?\s+(?:and|or)\s+[\w'-]+")
    hits = re.findall(pat, clean)
    rate = len(hits) / max(word_count(text), 200) * 200
    passed = rate <= max_per_200
    return {"id": "triads_ok", "severity": "soft", "passed": passed, "metric": round(rate, 2),
            "detail": f"{len(hits)} triad(s) ({rate:.2f}/200w). Examples: {hits[:2]}" if hits else "no triads"}


def check_no_throatclear_open(output: str, **kw) -> Dict:
    """SOFT: the first REAL sentence must start on point. A Subject: line (bold or
    plain), markdown emphasis, and a salutation line ('Hi Mark,') are skipped before
    judging; an inline greeting ('Hey team — ') is stripped from the first sentence."""
    text = _normalize(output).strip()
    text = _EMPHASIS.sub("", text)                                       # **Subject:** -> Subject:
    text = re.sub(r"^\s*subject\s*:[^\n]*\n+", "", text, flags=re.I)     # skip subject line
    text = re.sub(r"^\s*(?:hey|hi|hello)\b[^\n]{0,40}[,—–:-]\s*\n+", "", text, flags=re.I)
    sents = split_sentences(text)
    first = sents[0] if sents else ""
    first = re.sub(r"^\s*(?:hey|hi|hello)\b[^,—–-]{0,40}[,—–-]\s*", "", first, flags=re.I)
    for pat in THROATCLEAR_OPENERS:
        if re.search(pat, first, re.I):
            return {"id": "no_throatclear_open", "severity": "soft", "passed": False,
                    "detail": f"opens with runway: '{first[:60]}...'"}
    return {"id": "no_throatclear_open", "severity": "soft", "passed": True, "detail": "opens on point"}


def check_max_words(output: str, limit: int = 200, **kw) -> Dict:
    wc = word_count(output)
    return {"id": "max_words", "severity": "soft", "passed": wc <= limit, "metric": wc,
            "detail": f"{wc} words (limit {limit})"}


def check_has_subject(output: str, **kw) -> Dict:
    passed = bool(re.search(r"^\s*[*_]{0,3}subject[*_]{0,3}\s*:", _normalize(output), re.I | re.M))
    return {"id": "has_subject", "severity": "soft", "passed": passed,
            "detail": "subject line present" if passed else "no 'Subject:' line"}


def check_not_a_rewrite(output: str, source: str = "", **kw) -> Dict:
    """SOFT, metamorphic guard for Review mode: output should be feedback, not a rewrite.

    Measures how much of the OUTPUT's vocabulary comes from the source, after stripping
    quoted spans ('...' and "...") — quoting the source in feedback is citation, not
    rewriting. Sources under 8 distinct words are too short to assess.

    Honest residual limits: a synonym-level PARAPHRASE rewrite is lexically invisible
    here (that is the judge's restraint dimension), and a review that reuses source
    wording without quote marks still counts against the output."""
    if not source:
        return {"id": "not_a_rewrite", "severity": "soft", "passed": True, "detail": "no source provided"}
    so = set(w.lower() for w in _words(_normalize(source)))
    if len(so) < 8:
        return {"id": "not_a_rewrite", "severity": "soft", "passed": True,
                "detail": "source too short to assess"}
    out_clean = _strip_quoted(_normalize(output))
    oo = set(w.lower() for w in _words(out_clean))
    containment = len(so & oo) / max(len(oo), 1)
    passed = containment < 0.6
    return {"id": "not_a_rewrite", "severity": "soft", "passed": passed, "metric": round(containment, 2),
            "detail": f"{containment:.0%} of output vocabulary comes from the source (rewrite if high)"}


def check_no_onboarding_pitch(output: str, prompt: str = "", **kw) -> Dict:
    """SOFT: once a voice/influence profile exists, the skill must not re-pitch onboarding.
    Flags the setup/interview OFFER language — the 'offer once, never nag' rule made
    countable. If the PROMPT itself asks for setup, the pitch language is responsive,
    not a nag, and the check abstains."""
    if prompt and _ONBOARDING_REQUEST.search(_normalize(prompt)):
        return {"id": "no_onboarding_pitch", "severity": "soft", "passed": True,
                "detail": "user asked for onboarding — setup language is responsive, not a nag"}
    text = re.sub(r"\s+", " ", _normalize(output))
    hits = []
    for pat in ONBOARDING_PITCH:
        for m in re.finditer(pat, text, re.I):
            hits.append(m.group(0).strip())
    passed = len(hits) == 0
    return {"id": "no_onboarding_pitch", "severity": "soft", "passed": passed,
            "detail": "no onboarding re-pitch" if passed else f"re-pitches onboarding: {hits}"}


def check_zombie_nouns(output: str, threshold_per_200: float = 3.0, **kw) -> Dict:
    """SOFT: nominalization density — buried-verb nouns (-tion/-sion/-ment/-ance/-ence/-ity)
    per 200 words. Everyday nominalizations (information, documentation, implementation)
    are counted like any other; the threshold is tuned so plain prose passes and only a
    pileup ('the implementation of the migration required the utilization of...') flags.
    A 200-word floor keeps short notes from failing on a couple of ordinary words."""
    low = _normalize(output).lower()
    hits = _NOMINAL.findall(low)
    rate = len(hits) / max(word_count(output), 200) * 200
    passed = rate <= threshold_per_200
    detail = (f"{len(hits)} nominalization(s) ({rate:.2f}/200w): {sorted(set(hits))[:8]}"
              if hits else "no nominalization pileup")
    return {"id": "zombie_nouns", "severity": "soft", "passed": passed, "metric": round(rate, 2),
            "detail": detail}


def check_false_agency(output: str, **kw) -> Dict:
    """SOFT: false agency — inanimate subjects doing human things ('the data tells us',
    'this document outlines', 'the decision emerged'). A named human should own the verb.
    The pattern list is deliberately narrow for precision; the judge catches the rest."""
    text = re.sub(r"\s+", " ", _normalize(output))
    hits = []
    for pat in FALSE_AGENCY:
        for m in re.finditer(pat, text, re.I):
            hits.append(m.group(0))
    passed = len(hits) == 0
    return {"id": "false_agency", "severity": "soft", "passed": passed,
            "detail": "no false-agency phrasing" if passed else f"inanimate subjects with human verbs: {hits}"}


REGISTRY = {
    "no_invented_numbers": check_no_invented_numbers,
    "no_invented_quotes": check_no_invented_quotes,
    "no_invented_citations": check_no_invented_citations,
    "no_invented_urls": check_no_invented_urls,
    "no_high_conf_tells": check_no_high_conf_tells,
    "tell_flags": check_tell_flags,
    "formula_structures": check_formula_structures,
    "burstiness_ok": check_burstiness,
    "triads_ok": check_triads,
    "no_throatclear_open": check_no_throatclear_open,
    "max_words": check_max_words,
    "has_subject": check_has_subject,
    "not_a_rewrite": check_not_a_rewrite,
    "no_onboarding_pitch": check_no_onboarding_pitch,
    "zombie_nouns": check_zombie_nouns,
    "false_agency": check_false_agency,
}


def run(output: str, checks: List, prompt: str = "", source: str = "") -> List[Dict]:
    """checks: list of either 'id' strings or {'id':..., 'params':{...}} dicts.

    Raises ValueError for an unknown check id — a misspelled gate must fail the run
    loudly, never report green. Callers (run_checks.py, run_eval.py) catch it and
    report a hard failure."""
    output, prompt, source = _normalize(output), _normalize(prompt), _normalize(source)
    results = []
    for c in checks:
        if isinstance(c, str):
            cid, params = c, {}
        else:
            cid, params = c.get("id"), c.get("params", {})
        fn = REGISTRY.get(cid)
        if fn is None:
            raise ValueError(f"unknown check id: {cid!r} (registered: {sorted(REGISTRY)})")
        results.append(fn(output, prompt=prompt, source=source, **params))
    return results
