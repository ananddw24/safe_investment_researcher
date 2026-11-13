"""Run the Impact Calendar calculator checks with the real browser script."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "tests" / "js"


def test_impact_calendar_script_matches_the_worked_examples():
    node = shutil.which("node")
    npm = shutil.which("npm")
    assert node and npm, "node and npm are required to execute interactive.js"
    if not (JS_DIR / "node_modules" / "jsdom").exists():
        subprocess.run(["npm", "ci"], cwd=JS_DIR, check=True)
    subprocess.run(
        [node, "--test", "tests/js/impact_calendar.test.mjs"],
        cwd=ROOT,
        check=True,
    )
