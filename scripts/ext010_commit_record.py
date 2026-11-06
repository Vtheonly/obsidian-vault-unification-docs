#!/usr/bin/env python3
"""EXT-010: record the work commit hash in the task record and checkpoint
(EXT-009 two-commit pattern). Run AFTER the work commit exists."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUEUE = REPO / "state/task-queue.jsonl"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-10-27-ext-010.json"

work_commit = subprocess.run(
    ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, check=True).stdout.strip()

# task record
lines = QUEUE.read_text(encoding="utf-8").splitlines()
out = []
for line in lines:
    if not line.strip():
        continue
    rec = json.loads(line)
    if rec.get("task_id") == "EXT-010":
        assert rec.get("status") == "completed"
        assert rec.get("commit") in (None, "", "PENDING"), \
            f"commit already recorded: {rec.get('commit')}"
        rec["commit"] = work_commit
    out.append(json.dumps(rec, ensure_ascii=False, sort_keys=True))
QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")

# checkpoint
cp = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
assert cp["work_commit"] == "PENDING (recorded by the state commit)"
cp["work_commit"] = work_commit
CHECKPOINT.write_text(json.dumps(cp, indent=1, ensure_ascii=False) + "\n",
                      encoding="utf-8")

print(f"work commit {work_commit} recorded in task record and checkpoint")
