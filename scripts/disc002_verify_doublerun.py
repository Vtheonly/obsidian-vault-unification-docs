#!/usr/bin/env python3
"""DISC-002: verification double-run of the full-corpus discovery.

Re-runs discover_candidates over all 70 batches, writes to a scratch path,
compares sha256 with the first run (byte-identical requirement, REGEN-001
standard) and records peak RSS.
"""
from __future__ import annotations

import hashlib
import json
import resource
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vault_unification.discovery import discover_candidates  # noqa: E402

SCHEMA = REPO / "schemas" / "knowledge-unit.schema.json"
MANIFESTS = {
    "master-ai": REPO / "state/manifests" / "master-ai.jsonl",
    "ai-course": REPO / "state/manifests" / "ai-course.jsonl",
}
FIRST = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
SECOND = Path("/home/z/my-project/scratch/002-disc002-full-corpus-run2.jsonl")
PERF = REPO / "reports/discovery/disc002-full-corpus-perf.json"


def main() -> None:
    batches = [str(p) for p in sorted((REPO / "state/knowledge-units").glob("*.jsonl"))]
    t0 = time.monotonic()
    result = discover_candidates(batches, str(SCHEMA), MANIFESTS)
    dt = time.monotonic() - t0
    payload = "".join(
        json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n"
        for c in result["candidates"]
    )
    SECOND.write_text(payload, encoding="utf-8")

    first_digest = hashlib.sha256(FIRST.read_bytes()).hexdigest()
    second_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    perf = {
        "run": "verification double-run",
        "batches": len(batches),
        "kus": result["report"]["denominators"]["ku_records_loaded"],
        "seconds_run1": 547.4,
        "seconds_run2": round(dt, 1),
        "peak_rss_mb_run2": round(peak_mb, 1),
        "sha256_run1": first_digest,
        "sha256_run2": second_digest,
        "byte_identical": first_digest == second_digest,
        "candidates": len(result["candidates"]),
    }
    PERF.write_text(json.dumps(perf, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(perf))


if __name__ == "__main__":
    main()
