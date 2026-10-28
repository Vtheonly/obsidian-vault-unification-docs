#!/usr/bin/env python3
"""DISC-002: memory probe for the full-corpus discovery run.

Replicates discover_candidates' data structures stage by stage and reports
RSS after each stage, so an OOM kill can be attributed to a specific
structure. Read-only; writes nothing.
"""
from __future__ import annotations

import gc
import glob
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "src")


def rss_mb() -> float:
    with open("/proc/self/status") as fh:
        for line in fh:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return -1


def main() -> int:
    from vault_unification.discovery import _mine_ngrams, _term_text
    from vault_unification.overlap import load_ku_batches

    batches = sorted(p for p in glob.glob("state/knowledge-units/*.jsonl"))
    print(f"stage 0 start rss={rss_mb():.0f}MB batches={len(batches)}", flush=True)

    records = load_ku_batches(batches, "schemas/knowledge-unit.schema.json")
    print(f"stage 1 loaded {len(records)} KUs rss={rss_mb():.0f}MB", flush=True)

    ku_by_id = {rec["knowledge_unit_id"]: rec for rec in records}
    mined: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    pairs = 0
    for i, rec in enumerate(records):
        if rec["unit_type"] not in {
            "prose", "list", "table", "math_block", "callout", "quote", "code_block",
        }:
            continue
        grams = set(_mine_ngrams(rec["excerpt"]))
        for heading in rec.get("heading_path", []):
            for g in _mine_ngrams(heading):
                grams.add(g)
        for g in grams:
            mined[_term_text(g)][rec["knowledge_unit_id"]].append(rec)
            pairs += 1
        if i % 5000 == 0:
            print(f"  mining {i}/{len(records)} rss={rss_mb():.0f}MB", flush=True)
    print(
        f"stage 2 mined terms={len(mined)} pairs={pairs} rss={rss_mb():.0f}MB",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
