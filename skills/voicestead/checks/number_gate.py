#!/usr/bin/env python3
"""Voicestead invented-facts hard gate — the shipped, offline safety check.

SINGLE SOURCE OF TRUTH for the four invented-facts checks (numbers, quotes,
citations, URLs). It ships inside the skill so the offline `score_draft`
fallback can enforce the hard gate on code-capable surfaces (Claude Code,
skill-native CLIs). The dev harness tests/checks/text_metrics.py imports these
functions instead of keeping its own copy; tests/checks/test_gate_contract.py
fails CI on any divergence.

Pure stdlib. No network, ever. Each check returns:
    {"id": str, "severity": "hard", "passed": bool, "detail": str}
"""
import re
from typing import Dict, List, Tuple

# ---- unicode punctuation -> ascii (dashes deliberately untouched) ----
_PUNCT_MAP = {"'": "'", "'": "'", """: '"', """: '"'}


def _normalize(text: str) -> str:
    """Map unicode punctuation to ascii BEFORE any pattern matching."""
    for k, v in _PUNCT_MAP.items():
        text = text.replace(k, v)
    return text


def _words(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", s)


_WORD_NUMS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}


def _spelled_numbers(t: str) -> set:
    out = set()
    for m in re.finditer(r"\b([a-z]+)(?=[-\s]+([a-z]+)\b)?", t.lower()):
        a, b = m.group(1), m.group(2)
        if a in _WORD_NUMS:
            v = _WORD_NUMS[a]
            if b in _WORD_NUMS and v >= 20 and v % 10 == 0 and _WORD_NUMS[b] < 10:
                v += _WORD_NUMS[b]
            out.add(str(v))
    return out


_QUOTE_MIN_WORDS = 5


def _squash(t: str) -> str:
    return re.sub(r"\s+", " ", _normalize(t)).strip().lower()


_DQUOTE_SPAN = re.compile(r'"[^"]{0,300}"')
_SQUOTE_SPAN = re.compile(r"(?<!\w)'[^']{0,300}'(?!\w)")

_CIT_AUTHOR_YEAR = re.compile(
    r"\b([A-Z][A-Za-z'-]+)(?:\s+(?:et al\.?|&\s+[A-Z][A-Za-z'-]+|and\s+[A-Z][A-Za-z'-]+))?,?\s*\((\d{4})\)")
_CIT_BRACKET_REF = re.compile(r"\[(\d{1,3})\](?!\()")
_CIT_DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+")
_CIT_ACCORDING_TO = re.compile(r"\b[Aa]ccording to (?:the )?([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,3})")
_CIT_YEAR_STUDY = re.compile(r"\ba (\d{4}) (?:study|survey|report|paper|meta-analysis)\b", re.I)
_CIT_ENTITY_STOPWORDS = {"the", "a", "an", "of", "and", "new"}
_URL_ANY = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.I)


def _name_licensed(name: str, lic_words: set) -> bool:
    parts = _words(name)
    return bool(parts) and all(p.lower() in lic_words for p in parts)


def check_no_invented_numbers(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
    def toks(t):
        t = _normalize(t)
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
        t = re.sub(r"\[[^\]]*\]", " ", t)
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


def check_no_invented_citations(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
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


def check_no_invented_urls(output: str, prompt: str = "", source: str = "", **kw) -> Dict:
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


GATE_CHECKS = {
    "no_invented_numbers": check_no_invented_numbers,
    "no_invented_quotes": check_no_invented_quotes,
    "no_invented_citations": check_no_invented_citations,
    "no_invented_urls": check_no_invented_urls,
}


def gate(output: str, prompt: str = "", source: str = "") -> Tuple[bool, List[Dict]]:
    """Run all four hard checks. Returns (passed, failures)."""
    results = [fn(output, prompt=prompt, source=source) for fn in GATE_CHECKS.values()]
    failures = [r for r in results if not r["passed"]]
    return (len(failures) == 0, failures)
