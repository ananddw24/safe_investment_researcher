#!/usr/bin/env python3
from pathlib import Path
import re
import sys
urls = []
root = Path(__file__).resolve().parents[1]
for path in (root / "data" / "resources").rglob("*.yaml"):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"^url:\s*(\S+)", text, re.M):
        urls.append(m.group(1).strip("\"'"))
out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".lychee-inputs")
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "resource-urls.txt"
out.write_text("\n".join(sorted(set(urls))) + ("\n" if urls else ""), encoding="utf-8")
print(f"wrote {len(set(urls))} urls -> {out}")
