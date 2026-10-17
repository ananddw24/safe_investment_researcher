#!/usr/bin/env python3
"""Ensure resource and vehicle ids are unique across data/**/*.yaml."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SKIP_NAMES = {"_index.yaml", "_template.yaml"}


def main() -> int:
    seen: dict[str, list[Path]] = defaultdict(list)
    files = [
        p
        for p in sorted(DATA.rglob("*.yaml"))
        if p.name not in SKIP_NAMES and "schemas" not in p.parts
    ]
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "id" not in data:
            print(f"ERROR: {path} missing id", file=sys.stderr)
            return 1
        seen[str(data["id"])].append(path)

    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    if dupes:
        print("Duplicate ids found:", file=sys.stderr)
        for id_, paths in sorted(dupes.items()):
            joined = ", ".join(str(p) for p in paths)
            print(f"  - {id_}: {joined}", file=sys.stderr)
        return 1

    print(f"OK: {len(seen)} unique id(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
