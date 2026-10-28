#!/usr/bin/env python3
"""DISC-002: capture current-implementation output on a real subset.

Writes the 14-batch candidates file so the optimized implementation can be
proven byte-identical against it (regression evidence for the perf work).
"""
from __future__ import annotations

import hashlib
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
SUBSET = 14  # batches 001-014, ~3.5k KUs, mixed ext+regen provenance
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/home/z/my-project/scratch/baseline-subset14-candidates.jsonl"
)


def main() -> None:
    names = sorted(p.name for p in BATCH_DIR.glob("*.jsonl"))[:SUBSET]
    t0 = time.monotonic()
    result = discover_candidates(
        [str(BATCH_DIR / n) for n in names], str(SCHEMA), MANIFESTS
    )
    dt = time.monotonic() - t0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n"
        for c in result["candidates"]
    )
    OUT.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print(
        json.dumps(
            {
                "batches": len(names),
                "candidates": len(result["candidates"]),
                "seconds": round(dt, 1),
                "out": str(OUT),
                "sha256": digest,
                "bytes": len(payload.encode("utf-8")),
            }
        )
    )


if __name__ == "__main__":
    main()
