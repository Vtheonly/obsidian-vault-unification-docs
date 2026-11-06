#!/usr/bin/env python3
"""S28/SYNTH-001 gap treatments, phase A: replay the DISC-002 decision chain.

Regenerates the full-corpus candidates (deterministic discover-gaps, same
recorded args) and replays every committed decision round (r1, r2,
batch2..batch16, with their recorded decided-utc values) so the three
confirmed-gap candidates can be treated through the sanctioned
discovery-decide machinery in phase B (scripts/s28_gap_treatments.py).

Correctness proof: re-indexing the replayed post-batch16 state must be
CONTENT-IDENTICAL to the committed index
state/concept-candidates/002-disc002-full-corpus.index.jsonl (the same
check the batch16 replay performed).

Scratch outputs (git-ignored, regenerable):
  scratch/s28-gap/full.jsonl        discover-gaps output
  scratch/s28-gap/<round>.jsonl     post-round candidate states
  scratch/s28-gap/post-batch16.jsonl  final replayed state (phase B input)
  scratch/s28-gap/post-batch16.index.jsonl  re-index (verification only)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / "scratch" / "s28-gap"
SCRATCH.mkdir(parents=True, exist_ok=True)

RUN_ARGS = json.loads(
    (REPO / "reports/discovery/disc002-full-corpus-run.json").read_text()
)["report_meta"]["args"]

# recorded decided-utc per round (batch10/16 replay scripts + batch16 decide
# report reports/discovery/disc002-s16-batch16-decide.json)
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
    ("batch11", "state/concept-candidates/002-disc002-decisions-batch11.jsonl",
     "2026-10-31T08:00:00Z"),
    ("batch12", "state/concept-candidates/002-disc002-decisions-batch12.jsonl",
     "2026-10-31T10:30:00Z"),
    ("batch13", "state/concept-candidates/002-disc002-decisions-batch13.jsonl",
     "2026-10-31T13:30:00Z"),
    ("batch14", "state/concept-candidates/002-disc002-decisions-batch14.jsonl",
     "2026-11-01T03:30:00Z"),
    ("batch15", "state/concept-candidates/002-disc002-decisions-batch15.jsonl",
     "2026-11-01T04:15:00Z"),
    ("batch16", "state/concept-candidates/002-disc002-decisions-batch16.jsonl",
     "2026-11-01T22:30:00Z"),
]


def run(cmd: list[str]) -> dict:
    print("+", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"command failed: {cmd}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw": proc.stdout[:500]}


def main() -> int:
    t0 = time.time()
    # 1. regenerate the full-corpus candidates (recorded args; deterministic)
    full_out = SCRATCH / "full.jsonl"
    res = run([
        "vu", "discover-gaps",
        *[a for b in RUN_ARGS["batches"] for a in ("--batch", b)],
        *[a for m in RUN_ARGS["manifests"] for a in ("--manifest", m)],
        "--out", str(full_out),
        "--kus-schema", RUN_ARGS["kus_schema"],
        "--max-evidence", str(RUN_ARGS["max_evidence"]),
        "--report", "reports/discovery/s28-gap-replay-full.json",
    ])
    print(f"discover-gaps: {res.get('result', res).get('records_written', '?')} records "
          f"({time.time()-t0:.0f}s)")

    # 2. replay the 17 committed decision rounds
    current = full_out
    for name, decisions, decided_utc in DECIDE_CHAIN:
        t = time.time()
        nxt = SCRATCH / f"{name}.jsonl"
        res = run([
            "vu", "discovery-decide",
            "--candidates", str(current),
            "--decisions", decisions,
            "--out", str(nxt),
            "--candidate-schema", "schemas/concept-candidate.schema.json",
            "--decided-utc", decided_utc,
            "--report", f"reports/discovery/s28-gap-replay-{name}.json",
        ])
        r = res.get("result", res)
        print(f"{name}: {r.get('decisions_applied', '?')} decisions "
              f"({time.time()-t:.0f}s)")
        current = nxt

    # 3. rename the final state for phase B
    final = SCRATCH / "post-batch16.jsonl"
    final.write_bytes(current.read_bytes())

    # 4. verification: re-index must be content-identical to the committed index
    idx = SCRATCH / "post-batch16.index.jsonl"
    res = run([
        "vu", "discovery-index",
        "--candidates", str(final),
        "--out", str(idx),
        "--max-ku-ids", "12",
        "--report", "reports/discovery/s28-gap-replay-index.json",
    ])
    committed = (REPO / "state/concept-candidates/002-disc002-full-corpus.index.jsonl").read_bytes()
    replayed = idx.read_bytes()
    if committed == replayed:
        print("VERIFIED: replayed post-batch16 index is byte-identical to the committed index")
        return 0
    # diagnose differences
    a = [json.loads(l) for l in committed.read_text(encoding="utf-8").splitlines() if l.strip()]
    b = [json.loads(l) for l in replayed.decode("utf-8").splitlines() if l.strip()]
    print(f"MISMATCH: committed {len(a)} records vs replayed {len(b)}")
    da = {r["candidate_id"]: r for r in a}
    db = {r["candidate_id"]: r for r in b}
    diff = [k for k in set(da) | set(db) if da.get(k) != db.get(k)]
    print(f"differing records: {len(diff)}; first 5: {diff[:5]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
