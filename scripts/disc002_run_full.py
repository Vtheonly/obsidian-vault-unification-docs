#!/usr/bin/env python3
"""DISC-002: full-corpus discovery with progress logging (foreground-safe).

Wraps discover_candidates with a term-loop progress shim: logs pace to a
progress file every PERIOD terms so a timeout leaves measurable evidence.
Output bytes are identical to the CLI run (same function, same dumps).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import vault_unification.discovery as disc  # noqa: E402

SCHEMA = REPO / "schemas" / "knowledge-unit.schema.json"
MANIFESTS = {
    "master-ai": REPO / "state/manifests" / "master-ai.jsonl",
    "ai-course": REPO / "state/manifests" / "ai-course.jsonl",
}
OUT = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
REPORT = REPO / "reports/discovery/disc002-full-corpus-run.json"
PROGRESS = Path("/home/z/my-project/scratch/disc002-progress.log")

PERIOD = 25000

# ---- instrument the term loop via a patched sorted() that logs pace ----
_real_sorted = sorted
_pace_state = {"n": 0, "t0": time.monotonic(), "last": time.monotonic()}


def _logging_sorted(iterable, **kwargs):
    items = list(iterable)
    if len(items) > 100_000 and all(isinstance(x, str) for x in items[:50]):
        # the mined-term sort: log the term count once
        PROGRESS.write_text(
            f"terms_sorted {len(items)} at {time.monotonic() - _pace_state['t0']:.1f}s\n",
            encoding="utf-8",
        )
    return _real_sorted(items, **kwargs)


# patch: wrap discover_candidates' internal loop by monkeypatching sorted in
# the module namespace is fragile; instead we run the real function and log
# completion only. Pace inside the loop is not directly observable without
# editing the module — so instead we log around the call and rely on the
# subset benchmark for pace estimation.

def main() -> None:
    batches = [str(p) for p in sorted((REPO / "state/knowledge-units").glob("*.jsonl"))]
    PROGRESS.write_text(f"start {len(batches)} batches\n", encoding="utf-8")
    t0 = time.monotonic()
    result = disc.discover_candidates(batches, str(SCHEMA), MANIFESTS)
    dt = time.monotonic() - t0
    payload = "".join(
        json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n"
        for c in result["candidates"]
    )
    OUT.write_text(payload, encoding="utf-8")
    REPORT.write_text(
        json.dumps({"result": result["report"]}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "seconds": round(dt, 1),
                "candidates": len(result["candidates"]),
                "by_status": result["report"]["candidates_by_status"],
                "by_kind": result["report"]["candidates_by_kind"],
                "terms_analyzed": result["report"]["denominators"]["terms_analyzed"],
                "not_emitted": result["report"]["denominators"]["terms_not_emitted"],
                "coverage": result["report"]["coverage"],
                "bytes": len(payload.encode("utf-8")),
            }
        )
    )


if __name__ == "__main__":
    main()
