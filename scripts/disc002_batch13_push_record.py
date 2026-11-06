#!/usr/bin/env python3
"""DISC-002 session 13: record the push verification (state commit)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state/task-queue.jsonl"

PUSH_FROM = "c8fcfb8"
PUSH_TO = "ab4101a"
PUSH_RANGE = "c8fcfb8..ab4101a"
FEAT_COMMIT = "ab4101a"

records = []
with open(QUEUE, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))

push_note = (
    " SESSION-13 PUSH VERIFIED: the batch-13 feat commit "
    f"{FEAT_COMMIT} ('feat(DISC-002): batch-13 review tranche (60 decisions) "
    "+ thirteen-round ADR-0010 replay re-verification') was pushed to "
    f"origin/main ({PUSH_RANGE}) and verified with git fetch + rev-parse "
    "(HEAD == origin/main == ab4101a; clean tree) before this state commit. "
    "Session 12 is fully persisted."
)

for r in records:
    if r["task_id"] == "DISC-002":
        if push_note not in (r.get("notes") or ""):
            r["notes"] = (r.get("notes") or "") + push_note

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (session-13 push verification recorded)")

# also record in current-state notes
STATE = REPO / "state/current-state.json"
st = json.loads(STATE.read_text(encoding="utf-8"))
if "SESSION-13 PUSH VERIFIED" not in st["notes"]:
    st["notes"] = (
        st["notes"]
        + " SESSION-13 PUSH VERIFIED: feat commit ab4101a pushed to "
        "origin/main (c8fcfb8..ab4101a) and verified (HEAD == origin/main "
        "== ab4101a, clean tree) before this state commit."
    )
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated (session-13 push verification recorded)")
