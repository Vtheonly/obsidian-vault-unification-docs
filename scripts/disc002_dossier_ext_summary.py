#!/usr/bin/env python3
"""DISC-002 session 3: summarize the six-domain dossier-extension overlap runs.

Reads the six vu overlap-candidates reports (reports/dossier-ext/*.json) plus
the pair files in scratch, and writes a consolidated summary report with the
per-domain extension-funnel numbers, the exact replay commands, and the next
bounded action per the gap report's discipline (classification before dossier
regeneration; no bulk absorption of term matches).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/obsidian-vault-unification-docs")
SCRATCH = Path("/home/z/my-project/scratch")
REPORT_DIR = REPO / "reports/dossier-ext"
OUT = REPORT_DIR / "disc002-dext-summary.json"

DOMAINS = [
    "regression", "tree", "evaluation",
    "clustering", "generalization", "training-stability",
]

summary = {
    "task": "DISC-002 dossier extension — overlap-candidates runs (mechanical stage)",
    "generated_by": "scripts/disc002_dossier_ext_summary.py (session 3)",
    "method": (
        "vu overlap-candidates over the 59 regen KU batches (cross-vault: "
        "ai-course regen batches vs master-ai regen batches) with each domain's "
        "committed term map. Candidate pairs only — NO classification assigned. "
        "Pairs live in scratch (regenerable in ~40s per domain via the recorded "
        "command in each run report)."
    ),
    "next_action": (
        "Per domain, in bounded batches: (1) review candidate pairs with "
        "dossier-discipline semantic classification (the new-KU side must have "
        "real domain participation, not a broad-term hit); (2) extend the "
        "domain classification file (state/classifications/); (3) regenerate the "
        "dossier via scripts/ext006_dossiers.py with its rule set; (4) re-run "
        "--check byte-identity. Do NOT bulk-absorb term matches (gap report "
        "interpretation)."
    ),
    "domains": {},
}

for dom in DOMAINS:
    run = json.loads((REPORT_DIR / f"disc002-dext-{dom}-overlap-run.json").read_text())
    pairs_path = SCRATCH / f"dossier-ext-{dom}-pairs.jsonl"
    dossier = json.loads((REPO / "state/dossiers" / f"{dom.replace('tree', 'tree-based')}-v1.json").read_text()
                         if dom != "tree" else
                         (REPO / "state/dossiers" / "tree-based-v1.json").read_text())
    participants = set()
    for c in dossier["concepts"]:
        participants.update(c["ku_ids"])

    topics = Counter()
    new_kus = set()
    total = 0
    with open(pairs_path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            p = json.loads(line)
            total += 1
            topics[p["topic"]] += 1
            for side in ("ku_a", "ku_b"):
                if p[side]["ku_id"] not in participants:
                    new_kus.add(p[side]["ku_id"])
    at_cap = sorted(t for t, n in topics.items() if n >= 250)
    summary["domains"][dom] = {
        "term_map": run["report_meta"]["args"]["terms"].split("/")[-1],
        "pairs_total": total,
        "topics_total": len(topics),
        "topics_at_pair_cap_250": at_cap,
        "dossier_participating_kus": len(participants),
        "distinct_new_kus_in_pairs": len(new_kus),
        "pairs_file_scratch": str(pairs_path),
        "run_report": f"reports/dossier-ext/disc002-dext-{dom}-overlap-run.json",
    }

OUT.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
for dom, v in summary["domains"].items():
    print(f"  {dom:20s} pairs={v['pairs_total']:6d} topics={v['topics_total']:3d} "
          f"cap={len(v['topics_at_pair_cap_250']):2d} new_kus={v['distinct_new_kus_in_pairs']:5d}")
