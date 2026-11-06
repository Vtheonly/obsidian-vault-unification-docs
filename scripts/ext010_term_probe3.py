#!/usr/bin/env python3
"""EXT-010 probe round 3: context check for sense-collision terms.

Prints the short context windows where collision-prone terms occur in each
vault, so the term-map comment can document senses accurately and
classification can adjudicate with evidence.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCH_010 = REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl"
BATCH_011 = REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl"

TERMS = ["spikes", "noise", "attention", "BatchNorm", "Gaussian", "cycle",
         "critical", "identity", "plain", "norm", "bias", "batch", "scale",
         "epoch", "signal", "gain", "BPTT", "spike"]

def main() -> int:
    kus = []
    for path in (BATCH_010, BATCH_011):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))

    for term in TERMS:
        print(f"##### {term}")
        pat = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
        for r in kus:
            ex = r["excerpt"]
            for m in pat.finditer(ex):
                s = max(0, m.start() - 60)
                e = min(len(ex), m.end() + 60)
                ctx = ex[s:e].replace("\n", " | ")
                vault = r["source_id"].split(":", 1)[0]
                print(f"  [{vault} {r['knowledge_unit_id']}] ...{ctx}...")
                break  # one context per KU per term is enough
        print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
