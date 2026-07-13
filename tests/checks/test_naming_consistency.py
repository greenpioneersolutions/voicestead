import os, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    return open(os.path.join(REPO, rel), encoding="utf-8").read()


def test_beta_and_readme_name_the_connector():
    assert "Voicestead Memory" in _read("docs/BETA.md")
    assert "Voicestead Memory" in _read("README.md")


def test_no_api_voicestead_host_regressed():
    # The connector host is mcp.voicestead.ai; the old REST-style "api" host
    # variant must never reappear anywhere in the tree.
    needle = "api" + ".voicestead" + ".ai"   # assembled so this guard file can't match itself
    out = subprocess.run(["git", "grep", "-l", needle],
                         cwd=REPO, capture_output=True, text=True).stdout
    assert out.strip() == "", f"{needle} found in: {out}"
