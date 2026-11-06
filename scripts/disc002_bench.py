#!/usr/bin/env python3
"""DISC-002 benchmark: measure discover-gaps scaling on a KU subset.

Deterministic timing evidence for budgeting the full-corpus run.
Not part of the reusable framework (one-off task evidence).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vault_unification.discovery import discover_candidates  # noqa: E402

SCHEMA = REPO / "schemas" / "knowledge-unit.schema.json"
BATCH_DIR = REPO / "state" / "knowledge-units"
MANIFESTS = {
    "master-ai": REPO / "state" / "manifests" / "master-ai.jsonl",
    "ai-course": REPO / "state" / "manifests" / "ai-course.jsonl",
}


def load_batch_names() -> list[str]:
    return sorted(p.name for p in BATCH_DIR.glob("*.jsonl"))


def ku_count(path: Path) -> int:
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def main() -> None:
    names = load_batch_names()
    # benchmark ladder: ~5%, ~10%, ~20% of the corpus by KU count
    subsets = [names[:4], names[:7], names[:14]]
    for subset in subsets:
        kus = sum(ku_count(BATCH_DIR / n) for n in subset)
        t0 = time.monotonic()
        result = discover_candidates(
            [str(BATCH_DIR / n) for n in subset],
            str(SCHEMA),
            MANIFESTS,
        )
        dt = time.monotonic() - t0
        rep = result["report"]
        print(
            json.dumps(
                {
                    "batches": len(subset),
                    "ku_records": kus,
                    "seconds": round(dt, 1),
                    "terms_analyzed": rep["denominators"]["terms_analyzed"],
                    "candidates": rep["denominators"]["candidates_emitted"],
                    "by_status": rep["candidates_by_status"],
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
