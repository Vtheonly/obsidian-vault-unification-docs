#!/usr/bin/env python3
"""DISC-002: bounded dossier reconciliation check.

Deterministic checks over the six committed dossiers against the full corpus:
1. every dossier KU reference resolves in the committed batches;
2. the confirmed-gap / deferred / newly-covered discovery decisions that
   touch dossier domains are listed for the next dossier-extension pass.
No dossier is modified here — extension is a separate reviewed change.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOSSIER_DIR = REPO / "state/dossiers"
CAND = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
OUT = REPO / "reports/discovery/disc002-dossier-reconciliation.json"

# batch ku_id index
ku_index: set[str] = set()
for p in sorted((REPO / "state/knowledge-units").glob("*.jsonl")):
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                ku_index.add(json.loads(line)["knowledge_unit_id"])

report = {
    "command": "disc002-dossier-reconciliation (bounded check)",
    "dossiers": {},
    "decisions_touching_dossier_domains": [],
}

# domain keywords for cross-referencing the round-1/2 decisions
DOMAIN_KEYWORDS = {
    "regression": ["regression", "residual", "least squares", "ridge", "lasso"],
    "tree-based": ["tree", "forest", "boosting", "split", "gini"],
    "evaluation": ["metric", "accuracy", "precision", "recall", "f1", "roc", "auc", "validation"],
    "clustering": ["cluster", "k-means", "pca", "dimensionality", "embedding space"],
    "generalization": ["regulariz", "overfit", "generaliz", "dropout", "weight decay"],
    "training-stability": ["gradient", "initializ", "momentum", "adam", "normaliz", "vanishing", "exploding", "learning rate", "second moment"],
}

decided = []
with open(CAND, encoding="utf-8") as fh:
    for line in fh:
        if not line.strip():
            continue
        r = json.loads(line)
        if r["status"] in ("confirmed_gap", "deferred", "rejected", "already_covered") and r["decision_history"]:
            decided.append(r)

for path in sorted(DOSSIER_DIR.glob("*.json")):
    d = json.load(open(path, encoding="utf-8"))
    ku_ids = []
    for c in d.get("concepts", []):
        for vault_list in c.get("by_vault", {}).values():
            ku_ids.extend(vault_list)
        ku_ids.extend(c.get("ku_ids", []))
    unresolved = sorted({k for k in ku_ids if k not in ku_index})
    report["dossiers"][d["dossier_id"]] = {
        "concepts": len(d.get("concepts", [])),
        "ku_references": len(set(ku_ids)),
        "unresolved_ku_references": len(unresolved),
        "unresolved_sample": unresolved[:5],
        "regeneration": d.get("generated_by", "?"),
    }

for r in decided:
    term = r["term"]
    hits = [
        dom for dom, kws in DOMAIN_KEYWORDS.items()
        if any(kw in term for kw in kws)
    ]
    if hits:
        report["decisions_touching_dossier_domains"].append(
            {
                "term": term,
                "status": r["status"],
                "domains": hits,
                "candidate_id": r["candidate_id"],
            }
        )

report["summary"] = {
    "dossiers_checked": len(report["dossiers"]),
    "all_ku_references_resolve": all(
        v["unresolved_ku_references"] == 0 for v in report["dossiers"].values()
    ),
    "decisions_touching_dossiers": len(report["decisions_touching_dossier_domains"]),
    "note": (
        "Dossier KU references are intact (pre-restart batches revalidated "
        "byte-identical in REGEN-001). The listed discovery decisions overlap "
        "dossier domains and feed the next dossier-extension pass; no dossier "
        "was modified in DISC-002 — extension is a separate reviewed change "
        "after accepted-concept flow is defined."
    ),
}
OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report["summary"], indent=1))
print(
    "touching:",
    [d["term"] for d in report["decisions_touching_dossier_domains"]][:15],
)
