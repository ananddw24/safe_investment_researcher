"""Guards on published v1.2.0 copy: no internal job names, placeholder keys only."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED_WORD = "Mu" + "se"
BANNED_JOB = "financial-library-educator-reports-" + "weekly"
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".toml"}
SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}


def _public_texts():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path, path.read_text(encoding="utf-8", errors="replace")


def test_public_files_do_not_name_the_internal_job_system():
    hits = []
    for path, text in _public_texts():
        if re.search(rf"\b{BANNED_WORD}\b", text) or BANNED_JOB in text:
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_composed_configs_use_placeholders_and_the_pinned_imf_commit():
    pin = "316fcb14c33fc15afd54f6620a6a240143ef5d35"
    for name in ("claude-desktop-composed.json", "cursor-composed.json"):
        path = ROOT / "mcp-server" / "configs" / name
        doc = json.loads(path.read_text(encoding="utf-8"))
        text = path.read_text(encoding="utf-8")
        assert "YOUR_OWN_FREE_FRED_KEY" in text
        assert "your@email.example" in text
        assert "/path/to/safe_investment_researcher" in text
        assert pin in text
        assert doc["mcpServers"]["fred"]["command"] == "docker"
        assert doc["mcpServers"]["imf"]["command"] == "uvx"
        assert "stefanoamorelli/fred-mcp-server:latest" in doc["mcpServers"]["fred"]["args"]
        assert "stefanoamorelli/sec-edgar-mcp:latest" in doc["mcpServers"]["sec-edgar"]["args"]
        # A 32-character lowercase API-key shape, ignoring the pinned commit.
        leftovers = re.findall(r"\b[a-f0-9]{40}\b", text)
        assert leftovers
        assert set(leftovers) == {pin}
