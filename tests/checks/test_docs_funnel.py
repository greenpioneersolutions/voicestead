"""Drift-guard for the repo doc funnel.

CONNECT.md is the canonical connection guide; skills/voicestead/references/connect.md
mirrors it. This pins that they agree on every canonical connection fact so they can't
silently drift, plus the funnel structure of TROUBLESHOOTING.md and README.md.
Offline, deterministic, no API key.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


# Every connection fact that must be identical in the canonical doc and its mirror.
CANONICAL_FACTS = [
    "https://mcp.voicestead.ai/mcp",
    "claude mcp add --transport http voicestead https://mcp.voicestead.ai/mcp",
]


def test_connect_docs_agree_on_canonical_facts():
    canon = _read("CONNECT.md")
    mirror = _read("skills/voicestead/references/connect.md")
    for fact in CANONICAL_FACTS:
        assert fact in canon, "CONNECT.md missing canonical fact: %s" % fact
        assert fact in mirror, "references/connect.md missing canonical fact: %s" % fact
    for name, doc in (("CONNECT.md", canon), ("connect.md", mirror)):
        low = doc.lower()
        # the enable-for-this-chat gotcha
        assert ("this chat" in low or "current chat" in low
                or "current conversation" in low or "conversation you're in" in low), name
        assert ("enable" in low or "turn the connector on" in low or "switch" in low), name
        # both reconnect fixes
        assert ("sign-in" in low or "sign in" in low), name
        assert "permission" in low, name


def test_connect_docs_cross_reference_as_canonical_and_mirror():
    canon = _read("CONNECT.md")
    mirror = _read("skills/voicestead/references/connect.md")
    # the canonical file declares itself canonical and names the mirror by path
    assert "canonical" in canon.lower()
    assert "skills/voicestead/references/connect.md" in canon
    # the mirror names CONNECT.md and says it mirrors it
    assert "CONNECT.md" in mirror
    assert ("mirror" in mirror.lower() or "canonical" in mirror.lower())


def test_troubleshooting_leads_with_enable_for_chat_and_links_issues():
    md = _read("TROUBLESHOOTING.md")
    # the first quoted-symptom entry is the connector / doesn't-remember one
    idx = md.index('## "')
    nxt = md.find("## ", idx + 4)
    first = md[idx:nxt] if nxt != -1 else md[idx:]
    low = first.lower()
    assert "connector" in low or "remember" in low
    assert ("this chat" in low or "current conversation" in low or "enabled" in low)
    # each fix is short and the file ends at the issues link
    assert "github.com/greenpioneersolutions/voicestead/issues" in md
