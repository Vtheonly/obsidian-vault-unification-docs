#!/usr/bin/env python3
"""EXT-009: dump a readable digest of a KU batch for classification analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

batch = sys.argv[1]
out = sys.argv[2]
max_excerpt = int(sys.argv[3]) if len(sys.argv) > 3 else 10_000

records = []
for line in Path(batch).read_text(encoding="utf-8").splitlines():
    if line.strip():
        records.append(json.loads(line))

parts = []
for r in records:
    ex = r["excerpt"]
    if len(ex) > max_excerpt:
        ex = ex[:max_excerpt] + f"\n...[{len(r['excerpt']) - max_excerpt} chars truncated — READ SOURCE]"
    short_path = r["source_path"].split("/")[-1]
    parts.append(
        f"### {r['knowledge_unit_id']} [{r['unit_type']}] {short_path} L{r['line_start']}-{r['line_end']}\n{ex}\n"
    )

Path(out).write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {out}: {len(records)} KUs, {sum(len(p) for p in parts)} chars")
