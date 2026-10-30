#!/usr/bin/env python3
"""DISC-002 session 8: record the push blocker in task-queue and current-state.

The session-8 `git push origin main` failed: no GitHub credentials exist in
this environment (the PAT from earlier conversations is not persisted).
The work commit 6171b4f exists locally; this note records the honest state.
"""
from __future__ import annotations

import json
from pathlib import Path

QUEUE = Path("state/task-queue.jsonl")
STATE = Path("state/current-state.json")

lines = [l for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
records = [json.loads(l) for l in lines]
disc = next(r for r in records if r.get("task_id") == "DISC-002")
assert disc["status"] == "in_progress"

disc["notes"] += (
    " PUSH PENDING (session-8 end): git push origin main failed with 'could not "
    "read Username for https://github.com' — no credentials in this environment "
    "(no ~/.git-credentials, no ~/.netrc, no credential helper, no gh CLI, no "
    "GITHUB_TOKEN; the PAT used by sessions 1-7 is not persisted across "
    "sessions). Work commit 6171b4f (feat, all session-8 changes and state) "
    "exists locally on main; everything else this session is verified (663/663 "
    "final tests, both vaults byte-identical at start and end, committed index "
    "regenerated and delta-verified). No push verification is claimed. Next "
    "session first action: obtain the PAT, push, verify, and record "
    "reports/discovery/disc002-session8-push-verification.json."
)

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (push blocker); records:", len(records))

st = json.loads(STATE.read_text(encoding="utf-8"))
st["notes"] += (
    " PUSH PENDING: session-8 git push failed (no credentials in environment; "
    "the PAT from earlier conversations is not persisted). Work commit 6171b4f "
    "awaiting push; see checkpoint-2026-10-31-disc002-session8.json "
    "baseline_verification.push_status and the handoff SESSION-8 EXCEPTION."
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated (push blocker)")
