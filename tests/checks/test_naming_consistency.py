import os, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    return open(os.path.join(REPO, rel), encoding="utf-8").read()


def test_beta_and_readme_name_the_connector():
    assert "Voicestead Memory" in _read("docs/BETA.md")
    assert "Voicestead Memory" in _read("README.md")


def test_no_api_voicestead_host_regressed():
    # the connector host is mcp.voicestead.ai; api.voicestead.ai must never reappear
    out = subprocess.run(["git", "grep", "-l", "api.voicestead.ai"],
                         cwd=REPO, capture_output=True, text=True).stdout
    assert out.strip() == "", f"api.voicestead.ai found in: {out}"
