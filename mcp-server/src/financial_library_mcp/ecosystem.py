"""The curated ecosystem composition set, bundled with the server.

``ecosystem.json`` (next to this module) lists free MCP servers that
pair with FinancialLibrary — live official data (FRED, SEC EDGAR, IMF,
and more) to set against the library's curated explainers. The data is
curated by hand and checked on the date recorded in the file; servers
are referenced by configuration only, never vendored.
"""

from __future__ import annotations

import json
from pathlib import Path

_ECOSYSTEM_PATH = Path(__file__).with_name("ecosystem.json")


def load_ecosystem() -> dict:
    """Return the bundled ecosystem document as a dict."""
    with _ECOSYSTEM_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def list_servers(status: str | None = None) -> dict:
    """List ecosystem servers, optionally filtered by status.

    Status values: core, alternative, optional, pilot, advanced.
    """
    doc = load_ecosystem()
    servers = doc["servers"]
    if status is not None:
        servers = [s for s in servers if s["status"] == status]
    return {
        "checked": doc["checked"],
        "note": doc["note"],
        "count": len(servers),
        "servers": servers,
        "excluded": doc["excluded"],
    }
