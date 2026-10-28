#!/usr/bin/env python3
"""DISC-002 session 3: select the next bounded review tranche (batch 3).

Follows the handoff: individual evidence review, not class-based rejection.
Selection mirrors the established signal rules (fragmented_derivation OR
score >= 0.8 OR contexts >= 10), sorted by score desc, excluding candidates
that already have any decision in their history (reviewed in r1/r2/batch1/b2).

Writes:
- /home/z/my-project/scratch/disc002-batch3-brief.md  (review brief with quotes)
- /home/z/my-project/scratch/disc002-batch3-pool.json (pool stats)
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/obsidian-vault-unification-docs")
CAND = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
OUT = Path("/home/z/my-project/scratch/disc002-batch3-brief.md")
STATS = Path("/home/z/my-project/scratch/disc002-batch3-pool.json")

TRANCHE_SIZE = 60

records = []
with open(CAND, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))

prov = [r for r in records if r["status"] == "provisional_candidate"]
reviewed_ids = set()
for r in records:
    if r.get("decision_history"):
        reviewed_ids.add(r["candidate_id"])

unreviewed_prov = [r for r in prov if r["candidate_id"] not in reviewed_ids]

def tranche_rule(r: dict) -> bool:
    return (
        r["kind"] == "fragmented_derivation"
        or r["confidence"]["score"] >= 0.8
        or r["independent_contexts"] >= 10
    )

tranche = [r for r in unreviewed_prov if tranche_rule(r)]
tranche.sort(
    key=lambda r: (-r["confidence"]["score"], -r["independent_contexts"], r["term"])
)

pool_stats = {
    "provisional_total": len(prov),
    "unreviewed_provisional": len(unreviewed_prov),
    "unreviewed_matching_signal_rule": len(tranche),
    "by_kind": dict(Counter(r["kind"] for r in unreviewed_prov)),
    "score_histogram": dict(Counter(round(r["confidence"]["score"], 1) for r in unreviewed_prov)),
    "contexts_gte_10": sum(
        1 for r in unreviewed_prov if r["independent_contexts"] >= 10
    ),
    "cross_vault": sum(
        1 for r in unreviewed_prov if r["confidence"]["signals"]["cross_vault"]
    ),
}
STATS.write_text(json.dumps(pool_stats, indent=1) + "\n")

selected = tranche[:TRANCHE_SIZE]
lines = [
    "# DISC-002 review brief — session 3 tranche (batch 3)",
    f"unreviewed provisional pool: {len(unreviewed_prov)}; "
    f"signal-rule tranche: {len(tranche)}; selected: {len(selected)}",
    "",
]
for r in selected:
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
        q = e["quote"].replace("\n", " ")[:200]
        lines.append(
            f"  - [{e['relationship']}] {e['vault']}/{e['source_path']}:"
            f"{e['line_start']} — \"{q}\""
        )
    if r.get("homonym_clusters"):
        lines.append(f"  - homonym clusters: {len(r['homonym_clusters'])}")
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({k: v for k, v in pool_stats.items() if k != "score_histogram"}))
print(f"tranche selected: {len(selected)}; brief: {OUT}")
print("top score histogram:", dict(sorted(pool_stats["score_histogram"].items())[-6:]))
