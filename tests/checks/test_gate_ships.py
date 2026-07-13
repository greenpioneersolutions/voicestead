import os, sys, zipfile, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from scripts.package_skill import package


def test_number_gate_is_in_the_skill_archive():
    with tempfile.TemporaryDirectory() as d:
        out = package("voicestead", os.path.join(d, "voicestead.skill"))
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
    assert "voicestead/checks/number_gate.py" in names
    assert "voicestead/checks/__init__.py" in names
