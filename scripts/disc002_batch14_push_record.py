#!/usr/bin/env python3
"""DISC-002 session 14: record the push verification in task-queue + current-state.

Pattern: scripts/disc002_batch13_push_record.py (session 13). Verifies
HEAD == origin/main == d380dbc after the push and records the range
2d577cd..d380dbc in the DISC-002 queue notes and current-state notes.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"

EXPECTED_HEAD = "d380dbc"
PUSH_RANGE = "2d577cd..d380dbc"


def git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout.strip()


def main() -> int:
    head = git(["rev-parse", "--short", "HEAD"])
    origin = git(["rev-parse", "--short", "origin/main"])
    tree = [
        l for l in git(["status", "--porcelain"]).splitlines()
        # this script itself is expected to be untracked until the state commit
        if l.strip() != f"?? {Path(__file__).name}" and not l.strip().endswith("disc002_batch14_push_record.py")
    ]
    assert head == EXPECTED_HEAD, f"HEAD {head} != {EXPECTED_HEAD}"
    assert origin == EXPECTED_HEAD, f"origin/main {origin} != {EXPECTED_HEAD}"
    assert not tree, f"working tree not clean: {tree!r}"
    print(f"push verified: HEAD == origin/main == {head}; tree clean; range {PUSH_RANGE}")

    push_note = (
        f" SESSION-14 PUSH VERIFIED: feat commit d380dbc pushed to "
        f"origin/main ({PUSH_RANGE}); HEAD == origin/main == d380dbc, "
        f"working tree clean after the push."
    )

    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    queue = [json.loads(l) for l in lines if l.strip()]
    for t in queue:
        if t.get("task_id") == "DISC-002":
            if "SESSION-14 PUSH VERIFIED" not in t.get("notes", ""):
                t["notes"] = t.get("notes", "") + push_note
            break
    else:
        raise SystemExit("DISC-002 task not found")
    with open(QUEUE, "w", encoding="utf-8") as fh:
        for t in queue:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    if "SESSION-14 PUSH VERIFIED" not in state.get("notes", ""):
        state["notes"] = state.get("notes", "") + push_note
    STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("push verification recorded in task-queue and current-state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
