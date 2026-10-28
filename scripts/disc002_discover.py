#!/usr/bin/env python3
"""DISC-002 step 1: corpus-wide emergent-concept discovery over ALL 70 batches.

Runs `vu discover-gaps` over the complete committed KU corpus (all 70 batches,
609/609 source files, 27,536 KUs) with both vault manifests so the coverage
gate can evaluate coverage_complete=true. Output candidates go to
state/concept-candidates/002-disc002-full-corpus.jsonl and the run report to
reports/discovery/disc002-full-corpus-run.json.

Determinism contract (DISC-001): candidate ids are content-derived, records
sorted, no timestamps in candidate records; identical inputs regenerate
byte-identical output. This script double-runs the discovery and verifies
byte-identity before accepting the output (mirrors the REGEN-001 pattern).

Read-only with respect to both source vaults.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = "state/concept-candidates/002-disc002-full-corpus.jsonl"
REPORT = "reports/discovery/disc002-full-corpus-run.json"


def batch_args() -> list[str]:
    """All committed KU batches in numeric order (001-070)."""
    ku_dir = REPO_ROOT / "state" / "knowledge-units"
    batches = sorted(
        p.name for p in ku_dir.glob("*.jsonl") if p.name != "README.md"
    )
    if len(batches) != 70:
        print(f"FATAL: expected 70 batches, found {len(batches)}", file=sys.stderr)
        sys.exit(1)
    args: list[str] = []
    for name in batches:
        args.extend(["--batch", f"state/knowledge-units/{name}"])
    return args


def run_discovery(out_path: str, report_path: str) -> tuple[int, float, str]:
    cmd = [
        sys.executable,
        "-m",
        "vault_unification",
        "discover-gaps",
        *batch_args(),
        "--manifest",
        "master-ai=state/manifests/master-ai.jsonl",
        "--manifest",
        "ai-course=state/manifests/ai-course.jsonl",
        "--out",
        out_path,
        "--kus-schema",
        "schemas/knowledge-unit.schema.json",
        "--report",
        report_path,
    ]
    start = time.monotonic()
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=7200
    )
    elapsed = time.monotonic() - start
    return proc.returncode, elapsed, proc.stdout + proc.stderr


def main() -> int:
    import os

    tmp_out = "state/concept-candidates/.disc002-run2.tmp.jsonl"
    tmp_report = "reports/discovery/.disc002-run2.tmp.json"

    # run 1 — the accepted output (skippable when already on disk)
    if os.environ.get("DISC002_SKIP_RUN1") != "1":
        rc1, sec1, out1 = run_discovery(CANDIDATES, REPORT)
        print(f"run1 exit={rc1} seconds={sec1:.1f}", flush=True)
        if rc1 != 0:
            print(out1[-4000:], file=sys.stderr)
            return 1

    # run 2 — determinism check into temp paths
    rc2, sec2, out2 = run_discovery(tmp_out, tmp_report)
    print(f"run2 exit={rc2} seconds={sec2:.1f}", flush=True)
    if rc2 != 0:
        print(out2[-4000:], file=sys.stderr)
        return 1

    a = (REPO_ROOT / CANDIDATES).read_bytes()
    b = (REPO_ROOT / tmp_out).read_bytes()
    if a != b:
        print("FATAL: double-run not byte-identical", file=sys.stderr)
        return 1
    (REPO_ROOT / tmp_out).unlink()
    (REPO_ROOT / tmp_report).unlink()
    print("determinism: byte-identical double-run OK")

    # summarize the accepted report
    import json

    report = json.loads((REPO_ROOT / REPORT).read_text(encoding="utf-8"))
    res = report["result"]
    print("coverage:", json.dumps(res["coverage"]))
    print("candidates:", res["denominators"]["candidates_emitted"])
    print("by_kind:", json.dumps(res["candidates_by_kind"]))
    print("by_status:", json.dumps(res["candidates_by_status"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
