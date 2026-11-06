#!/usr/bin/env python3
"""DISC-002 session 5: select the next bounded review tranche (batch 5).

Same signal rules as batches 3-4 (fragmented_derivation OR score >= 0.8 OR
contexts >= 10), sorted by score desc, excluding candidates that already
have any decision in their history (reviewed in r1/r2/batch2/batch3/batch4).

Repo-relative; reads the session-5 replayed candidates (content-identical
to the committed index state) from scratch.

Writes:
- /home/z/my-project/scratch/disc002-batch5-brief.md  (review brief with quotes)
- /home/z/my-project/scratch/disc002-batch5-pool.json (pool stats)
- /home/z/my-project/scratch/disc002-batch5-selected.json (candidate_id + term
  list in selection order, for the decisions step)
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAND = Path("/home/z/my-project/scratch/disc002-s5-batch4.jsonl")
OUT = Path("/home/z/my-project/scratch/disc002-batch5-brief.md")
STATS = Path("/home/z/my-project/scratch/disc002-batch5-pool.json")
SELECTED = Path("/home/z/my-project/scratch/disc002-batch5-selected.json")

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
SELECTED.write_text(
    json.dumps(
        [
            {
                "candidate_id": r["candidate_id"],
                "term": r["term"],
                "kind": r["kind"],
                "score": r["confidence"]["score"],
                "contexts": r["independent_contexts"],
            }
            for r in selected
        ],
        indent=1,
    )
    + "\n"
)

lines = [
    "# DISC-002 review brief — session 5 tranche (batch 5)",
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
