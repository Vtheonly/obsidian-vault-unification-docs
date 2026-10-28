#!/usr/bin/env python3
"""DISC-002 session 3: compact the six dossier-ext overlap run reports.

The vu overlap-candidates report embeds the full pairs/evidence lists
(redundant with the pairs JSONL, which is regenerable in ~40s/domain via the
recorded command). Per ADR-0010 convention (heavy derived artifacts stay out
of git when replayable), strip the heavy lists and keep counts, scope, method,
topic keys, and truncated-topic flags. The stripping is recorded in the
report itself (`compact_notes`).
"""
from __future__ import annotations

import json
from pathlib import Path

REPORT_DIR = Path("/home/z/my-project/obsidian-vault-unification-docs/reports/dossier-ext")
STRIP_KEYS = ("pairs", "exact_hash_pairs", "normalized_hash_pairs")
DOMAINS = ["regression", "tree", "evaluation", "clustering",
           "generalization", "training-stability"]

for dom in DOMAINS:
    p = REPORT_DIR / f"disc002-dext-{dom}-overlap-run.json"
    d = json.loads(p.read_text())
    stripped = {}
    for k in STRIP_KEYS:
        if k in d.get("result", {}):
            stripped[k] = len(d["result"][k])
            del d["result"][k]
    d["compact_notes"] = (
        "heavy evidence lists stripped per ADR-0010 convention (full detail "
        "regenerable via the recorded command in report_meta.args; pairs JSONL "
        f"in scratch): " + json.dumps(stripped)
    )
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{dom}: stripped {stripped} -> {p.stat().st_size // 1024} KB")
