#!/usr/bin/env python3
"""EXT-010: concatenate the per-file part batches in fixed order.

Batch 010 (master-ai) = 07 Initialization Schemes, then 08 Vanishing and
Exploding Gradients.
Batch 011 (ai-course)  = 01 Weight Initialization, then 02 Weight
Initialization Techniques, then 03 The Vanishing and Exploding Gradient
Problems.

Each part was double-run and verified byte-identical before concatenation
(reports/extraction/ext010-coverage-*.json). The concatenated batches are
regenerated deterministically by this script (fixed order, no edits).
"""
import json
from pathlib import Path

PARTS_DIR = Path("/home/z/my-project/ext010-parts")
REPO = Path(__file__).resolve().parents[1]

BATCHES = [
    (
        [
            "run1-07-initialization-schemes.jsonl",
            "run1-08-vanishing-exploding.jsonl",
        ],
        REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl",
    ),
    (
        [
            "run1-01-weight-init.jsonl",
            "run1-02-init-techniques.jsonl",
            "run1-03-vanishing-exploding.jsonl",
        ],
        REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl",
    ),
]

for parts, out in BATCHES:
    total = 0
    by_part = {}
    with open(out, "w", encoding="utf-8") as fout:
        for p in parts:
            n = 0
            with open(PARTS_DIR / p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        fout.write(line)
                        n += 1
            by_part[p] = n
            total += n
    # verify every line parses and count types
    types = {}
    ids = set()
    dup = 0
    for line in open(out, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        t = rec.get("unit_type", "?")
        types[t] = types.get(t, 0) + 1
        if rec["knowledge_unit_id"] in ids:
            dup += 1
        ids.add(rec["knowledge_unit_id"])
    print(out.name)
    print("  per part:", by_part)
    print("  total records:", total, "| unique ids:", len(ids), "| duplicate ids:", dup)
    print("  units_by_type:", dict(sorted(types.items())))
