#!/usr/bin/env python3
"""Export resource YAML records to site_json/resources.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "data" / "resources"
OUT_DIR = ROOT / "site_json"
OUT_FILE = OUT_DIR / "resources.json"
SKIP_NAMES = {"_index.yaml", "_template.yaml"}


def main() -> int:
    records = []
    for path in sorted(RESOURCES_DIR.rglob("*.yaml")):
        if path.name in SKIP_NAMES:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            print(f"ERROR: {path} is not a mapping", file=sys.stderr)
            return 1
        records.append(data)

    records.sort(key=lambda r: r.get("id", ""))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} resource(s) to {OUT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
