#!/usr/bin/env python3
"""EXT-009: concatenate the three ai-course part batches in fixed order (05, 06, 07)."""
import json

PARTS = [
    "/tmp/ext009-run1-05. Batch Normalization.jsonl",
    "/tmp/ext009-run1-06. Dropout and Regularization.jsonl",
    "/tmp/ext009-run1-07. Data Augmentation.jsonl",
]
OUT = "state/knowledge-units/009-ext009-ai-course-04.3-regularization.jsonl"

total = 0
by_part = {}
with open(OUT, "w", encoding="utf-8") as out:
    for p in PARTS:
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.write(line)
                    n += 1
        by_part[p.split("-run1-")[1]] = n
        total += n

print("per part:", by_part)
print("total records:", total)

# validate every line parses and count types
types = {}
for line in open(OUT, encoding="utf-8"):
    if not line.strip():
        continue
    rec = json.loads(line)
    t = rec.get("unit_type", "?")
    types[t] = types.get(t, 0) + 1
print("units_by_type:", dict(sorted(types.items())))
