#!/usr/bin/env python3
"""Assemble blind A/B pairs for the Tier-3 human pass (PROTOCOL.md, Path B). No key.

Path B of the golden protocol asks a human "which would you actually send?" for each
with-skill vs without-skill pair, with the labels stripped so the answer isn't biased.
Doing that by hand is fiddly and easy to spoil. This script does it:

  * reads a results dir holding NN-with.txt / NN-without.txt for each piece,
  * for every pair, randomly assigns the two outputs to slot A and slot B,
  * writes blind-pairs.md (A and B only, no with/without labels) for the human to score,
  * saves the un-blinding key to a HIDDEN dotfile (.answers.json) so a casual open of the
    results dir doesn't reveal which side was the skill.

  python tests/golden/assemble_blind_pairs.py tests/golden/results
  # ...score blind-pairs.md by hand, then reveal with the key:
  python -c "import json;print(json.load(open('tests/golden/results/.answers.json'))['key'])"

Filenames: any pair `<stem>-with.txt` + `<stem>-without.txt` is matched on <stem>, so
`01-with.txt`/`01-without.txt` and `03-linkedin-with.txt`/`03-linkedin-without.txt` both work.
Pass --seed for a reproducible shuffle (handy for tests); omit it for real blind review.
"""
import argparse
import glob
import json
import os
import random
import sys
from datetime import datetime, timezone


def _discover_pairs(results_dir):
    """{stem: (with_path, without_path)} for every stem that has both files."""
    withs, withouts = {}, {}
    for path in glob.glob(os.path.join(results_dir, "*-with.txt")):
        withs[os.path.basename(path)[:-len("-with.txt")]] = path
    for path in glob.glob(os.path.join(results_dir, "*-without.txt")):
        withouts[os.path.basename(path)[:-len("-without.txt")]] = path
    pairs = {}
    for stem in sorted(set(withs) & set(withouts)):
        pairs[stem] = (withs[stem], withouts[stem])
    lonely = sorted(set(withs) ^ set(withouts))
    return pairs, lonely


def _read(path):
    with open(path) as f:
        return f.read().strip()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results_dir", help="dir holding NN-with.txt / NN-without.txt pairs")
    ap.add_argument("--out", default=None, help="blind sheet path (default <results_dir>/blind-pairs.md)")
    ap.add_argument("--key", default=None, help="hidden key path (default <results_dir>/.answers.json)")
    ap.add_argument("--seed", type=int, default=None, help="seed the A/B shuffle for a reproducible sheet")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.results_dir):
        ap.error("no such results dir: %s" % args.results_dir)
    out_path = args.out or os.path.join(args.results_dir, "blind-pairs.md")
    key_path = args.key or os.path.join(args.results_dir, ".answers.json")

    pairs, lonely = _discover_pairs(args.results_dir)
    if not pairs:
        ap.error("no NN-with.txt / NN-without.txt pairs found in %s" % args.results_dir)
    for stem in lonely:
        print("warning: %s is missing its with/without partner - skipped" % stem, file=sys.stderr)

    rng = random.Random(args.seed)
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    key = {}
    md = ["# Blind pairs - which would you actually send?",
          "",
          "_Generated %s from `%s`._" % (ts, args.results_dir),
          "",
          "For each piece, read A and B, then record: **send** (A / B / tie), **ship?** (y / n),",
          "and **me?** (y / n) - does it sound like you. The with-skill / without-skill labels are",
          "hidden in `%s`; score every piece before you unblind." % os.path.basename(key_path),
          ""]

    for stem in sorted(pairs):
        with_path, without_path = pairs[stem]
        with_is_a = rng.random() < 0.5
        a_path, b_path = (with_path, without_path) if with_is_a else (without_path, with_path)
        key[stem] = {"A": "with" if with_is_a else "without",
                     "B": "without" if with_is_a else "with"}
        md += ["## Piece %s" % stem,
               "",
               "### A",
               "",
               _read(a_path),
               "",
               "### B",
               "",
               _read(b_path),
               "",
               "**send:** ______  ·  **ship?** ______  ·  **me?** ______",
               "",
               "---",
               ""]

    with open(out_path, "w") as f:
        f.write("\n".join(md))
    with open(key_path, "w") as f:
        json.dump({"generated": ts, "results_dir": os.path.abspath(args.results_dir),
                   "seed": args.seed, "key": key}, f, indent=2)

    print("assembled %d blind pair(s) -> %s" % (len(pairs), out_path))
    print("un-blinding key (do not peek until scored) -> %s" % key_path)


if __name__ == "__main__":
    main()
