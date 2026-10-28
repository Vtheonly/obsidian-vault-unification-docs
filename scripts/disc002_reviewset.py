#!/usr/bin/env python3
"""DISC-002: extract a prioritized review working set from the full-corpus
candidates file (full evidence quotes included) for semantic review.

Writes:
- state/concept-candidates/.disc002-review-workingset.jsonl (full records)
- stdout: compact listing for the reviewer
"""
from __future__ import annotations

import json
from pathlib import Path

FULL = Path("state/concept-candidates/002-disc002-full-corpus.jsonl")
OUT = Path("state/concept-candidates/.disc002-review-workingset.jsonl")

# Bounded, deterministic selection rules:
# 1. ALL fragmented_derivation candidates with score >= 0.85
# 2. unexplained_prerequisite with score >= 0.90 and cross_vault
# 3. rare_essential with score >= 0.90
RULES = [
    ("fd-high", lambda r: r["kind"] == "fragmented_derivation"
     and r["confidence"]["score"] >= 0.85),
    ("up-crossvault-high", lambda r: r["kind"] == "unexplained_prerequisite"
     and r["confidence"]["score"] >= 0.90
     and r["confidence"]["signals"]["cross_vault"]),
    ("re-high", lambda r: r["kind"] == "rare_essential"
     and r["confidence"]["score"] >= 0.90),
]

selected: list[tuple[str, dict]] = []
counts = {name: 0 for name, _ in RULES}
with open(FULL, encoding="utf-8") as fh:
    for line in fh:
        if not line.strip():
            continue
        rec = json.loads(line)
        for name, rule in RULES:
            if rule(rec):
                selected.append((name, rec))
                counts[name] += 1
                break

OUT.write_text(
    "".join(json.dumps(rec, sort_keys=True) + "\n" for _, rec in selected),
    encoding="utf-8",
)
print(f"selected {len(selected)} candidates: {counts}")
for name, rec in selected:
    sig = rec["confidence"]["signals"]
    print(
        f"[{name}] {rec['candidate_id']} score={rec['confidence']['score']} "
        f"ic={rec['independent_contexts']} def={sig['definition_count']} "
        f"xvault={sig['cross_vault']} homonym={rec['homonym_suspect']} "
        f"term={rec['term']!r}"
    )
