#!/usr/bin/env python3
"""DISC-002 session 11 (batch 11): replay the ADR-0010 chain into scratch.

Repo-relative helper that drives the CLI (extends
scripts/disc002_batch10_replay.py with the batch-10 decide round — the
chain is now ELEVEN decide rounds):

1. `vu discover-gaps` over all 70 recorded batches (exact args from
   reports/discovery/disc002-full-corpus-run.json report_meta.args)
   -> scratch/disc002-s11-full.jsonl
2. `vu discovery-decide` for r1 (2026-10-28T00:45:00Z),
   r2 (01:30:00Z), batch2 (02:30:00Z), batch3 (2026-10-28T05:30:00Z),
   batch4 (2026-10-30T13:05:00Z), batch5 (15:30:00Z), batch6 (16:30:00Z),
   batch7 (2026-10-31T00:30:00Z), batch8 (2026-10-31T01:30:00Z),
   batch9 (2026-10-31T03:00:00Z), batch10 (2026-10-31T05:30:00Z)
   -> scratch/disc002-s11-batch10.jsonl  (post-batch10 full state; the
   starting point for the batch-11 review tranche)
3. `vu discovery-index` on the result -> scratch index, then
   CONTENT-compare (F-0019: parsed records, not raw bytes) against the
   committed state/concept-candidates/002-disc002-full-corpus.index.jsonl.

Expected post-batch10 statuses: 60,154 records;
51,552 provisional / 7,115 already_covered / 1,482 rejected /
3 confirmed_gap (second moment, bradley-terry, async def) /
1 merged / 1 deferred.

The corpus-wide discover-gaps step takes ~5 minutes; run this script as a
single tool call (F-0016: long runs must fit one tool call).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = Path("/home/z/my-project/scratch")
SCRATCH.mkdir(parents=True, exist_ok=True)

RUN_ARGS = json.loads(
    (REPO / "reports/discovery/disc002-full-corpus-run.json").read_text()
)["report_meta"]["args"]

DECIDE_CHAIN = [
    ("r1", "state/concept-candidates/002a-disc002-decisions-r1.jsonl",
     "2026-10-28T00:45:00Z"),
    ("r2", "state/concept-candidates/002b-disc002-decisions-r2.jsonl",
     "2026-10-28T01:30:00Z"),
    ("batch2", "state/concept-candidates/002-disc002-decisions-batch2.jsonl",
     "2026-10-28T02:30:00Z"),
    ("batch3", "state/concept-candidates/002-disc002-decisions-batch3.jsonl",
     "2026-10-28T05:30:00Z"),
    ("batch4", "state/concept-candidates/002-disc002-decisions-batch4.jsonl",
     "2026-10-30T13:05:00Z"),
    ("batch5", "state/concept-candidates/002-disc002-decisions-batch5.jsonl",
     "2026-10-30T15:30:00Z"),
    ("batch6", "state/concept-candidates/002-disc002-decisions-batch6.jsonl",
     "2026-10-30T16:30:00Z"),
    ("batch7", "state/concept-candidates/002-disc002-decisions-batch7.jsonl",
     "2026-10-31T00:30:00Z"),
    ("batch8", "state/concept-candidates/002-disc002-decisions-batch8.jsonl",
     "2026-10-31T01:30:00Z"),
    ("batch9", "state/concept-candidates/002-disc002-decisions-batch9.jsonl",
     "2026-10-31T03:00:00Z"),
    ("batch10", "state/concept-candidates/002-disc002-decisions-batch10.jsonl",
     "2026-10-31T05:30:00Z"),
]


def run(cmd: list[str]) -> dict:
    print("+", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"command failed: {cmd}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw": proc.stdout}


def content_lines(path: Path) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def main() -> int:
    steps: list[dict] = []

    # 1. regenerate the full-corpus candidates (CLI writer; F-0019 applies)
    full_out = SCRATCH / "disc002-s11-full.jsonl"
    report = REPO / "reports/discovery" / "disc002-s11-replay-full.json"
    res = run([
        "vu", "discover-gaps",
        *[a for b in RUN_ARGS["batches"] for a in ("--batch", b)],
        *[a for m in RUN_ARGS["manifests"] for a in ("--manifest", m)],
        "--out", str(full_out),
        "--kus-schema", RUN_ARGS["kus_schema"],
        "--max-evidence", str(RUN_ARGS["max_evidence"]),
        "--report", str(report),
    ])
    steps.append({"step": "discover-gaps", "result": res})

    # 2. replay the eleven decision rounds
    current = full_out
    for name, decisions, decided_utc in DECIDE_CHAIN:
        nxt = SCRATCH / f"disc002-s11-{name}.jsonl"
        rep = REPO / "reports/discovery" / f"disc002-s11-replay-{name}.json"
        res = run([
            "vu", "discovery-decide",
            "--candidates", str(current),
            "--decisions", decisions,
            "--out", str(nxt),
            "--candidate-schema", "schemas/concept-candidate.schema.json",
            "--decided-utc", decided_utc,
            "--report", str(rep),
        ])
        steps.append({"step": f"decide-{name}", "result": res})
        current = nxt

    # 3. index the replayed chain result and content-compare vs committed
    s11_index = SCRATCH / "disc002-s11-batch10.index.jsonl"
    rep = REPO / "reports/discovery" / "disc002-s11-replay-index.json"
    res = run([
        "vu", "discovery-index",
        "--candidates", str(current),
        "--out", str(s11_index),
        "--max-ku-ids", "12",
        "--report", str(rep),
    ])
    steps.append({"step": "index", "result": res})

    committed = REPO / "state/concept-candidates/002-disc002-full-corpus.index.jsonl"
    a = content_lines(s11_index)
    b = content_lines(committed)
    identical = a == b
    from collections import Counter
    status_counts = Counter(r["status"] for r in a)
    print("index content-identical to committed:", identical)
    print("status counts:", dict(status_counts))
    print("records:", len(a), "vs committed", len(b))

    # 4. validate the replayed candidates
    res = run([
        "vu", "discovery-validate",
        "--candidates", str(current),
        "--candidate-schema", "schemas/concept-candidate.schema.json",
        "--report", str(REPO / "reports/discovery" / "disc002-s11-replay-validate.json"),
    ])
    steps.append({"step": "validate", "result": res})

    (SCRATCH / "disc002-s11-replay-summary.json").write_text(
        json.dumps({
            "identical_to_committed_index": identical,
            "records": len(a),
            "status_counts": dict(status_counts),
            "steps": steps,
        }, indent=1) + "\n"
    )
    print("replay summary saved:", SCRATCH / "disc002-s11-replay-summary.json")
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
