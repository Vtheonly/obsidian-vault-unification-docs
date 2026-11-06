#!/usr/bin/env python3
"""DISC-002: build the individual-review brief for the top candidates.

Extracts the review tranche (highest-signal provisional candidates) with
full evidence quotes for semantic review. Pure extraction — no decisions.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAND = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
OUT = Path("/home/z/my-project/scratch/disc002-review-brief-r2.md")

records = []
with open(CAND, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))
prov = [r for r in records if r["status"] == "provisional_candidate"]

# tranche: fragmented_derivation OR score >= 0.8 OR contexts >= 10
tranche = [
    r for r in prov
    if r["kind"] == "fragmented_derivation"
    or r["confidence"]["score"] >= 0.8
    or r["independent_contexts"] >= 10
]
tranche.sort(key=lambda r: (-r["confidence"]["score"], -r["independent_contexts"], r["term"]))

lines = [
    "# DISC-002 individual review brief (tranche r2)",
    f"provisional pool: {len(prov)}; tranche size: {len(tranche)}",
    "",
]
for r in tranche[:60]:
    sig = r["confidence"]["signals"]
    lines.append(f"## {r['term']}  [{r['candidate_id']}]")
    lines.append(
        f"- kind={r['kind']} contexts={r['independent_contexts']} "
        f"score={r['confidence']['score']} cross_vault={sig['cross_vault']} "
        f"assumed={sig['assumed_usages']} deriv={sig['derivation_usages']} "
        f"homonym={r['homonym_suspect']} copied={r['copied_passage']}"
    )
    lines.append(f"- destination hint: {r['destination_recommendation']}")
    for e in r["evidence"][:4]:
        q = e["quote"].replace("\n", " ")[:220]
        lines.append(
            f"  - [{e['relationship']}] {e['vault']}/{e['source_path']}:"
            f"{e['line_start']} — \"{q}\""
        )
    if r.get("homonym_clusters"):
        lines.append(f"  - homonym clusters: {len(r['homonym_clusters'])}")
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"tranche={len(tranche)} brief_chars={len(chr(10).join(lines))}")
