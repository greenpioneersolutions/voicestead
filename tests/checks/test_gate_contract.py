"""The shipped gate and the dev harness must agree, verdict-for-verdict, forever."""
import os, sys, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)                                             # text_metrics
sys.path.insert(0, os.path.join(REPO, "skills", "voicestead", "checks"))  # number_gate
import text_metrics as tm
import number_gate as ng

GATE_IDS = ["no_invented_numbers", "no_invented_quotes",
            "no_invented_citations", "no_invented_urls"]

CASES = [
    ("We grew 47% last quarter.", "write about growth", ""),
    ("We grew 47%.", "we grew 47%, write it up", ""),
    ("Here are 3 options.", "give me options", ""),
    ('She said "best launch we have ever run".', "write about the launch", ""),
    ("Sign up at https://example.com/x today.", "announce signup", ""),
    ("As Alvarez (2021) showed.", "write about method", ""),
    ("Revenue hit $9M per [1] and 2026 looks strong.", "summarize the numbers", ""),
]


def test_text_metrics_delegates_to_shipped_gate():
    for output, prompt, source in CASES:
        tm_results = {r["id"]: r for r in tm.run(output, GATE_IDS, prompt=prompt, source=source)}
        for cid, fn in ng.GATE_CHECKS.items():
            assert tm_results[cid] == fn(output, prompt=prompt, source=source), (cid, output)


def test_contract_holds_on_the_corpus():
    for manifest in glob.glob(os.path.join(REPO, "tests", "corpus", "*.json")):
        spec = json.load(open(manifest))
        out_path = os.path.join(os.path.dirname(manifest), spec["output_file"])
        output = open(out_path).read()
        prompt = spec.get("prompt", "")
        source = spec.get("source", "")
        tm_results = {r["id"]: r for r in tm.run(output, GATE_IDS, prompt=prompt, source=source)}
        for cid, fn in ng.GATE_CHECKS.items():
            assert tm_results[cid] == fn(output, prompt=prompt, source=source), (cid, manifest)
