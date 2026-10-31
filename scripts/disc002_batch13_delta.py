#!/usr/bin/env python3
"""DISC-002 session 13 (batch 12): post-decide delta verification.

Compares scratch/disc002-s13-batch12.jsonl (pre) with
scratch/disc002-s13-batch13.jsonl (post) record-by-record (by candidate_id):
- exactly 60 status changes are expected (30 provisional->already_covered,
  30 provisional->rejected), matching the intended actions;
- decision_history must be appended for all 60 changed records;
- all other 60,094 records must be byte-identical;
- final status counts must equal 51,372/7,197/1,580/3/1/1
  (provisional/already_covered/rejected/confirmed_gap/merged/deferred).

Expectation arithmetic written down BEFORE running (delta-verification
discipline, session 11): pre-batch13 counts were 51,432/7,167/1,550/3/1/1;
this tranche applies 30 covers (+30 already_covered) and 30 rejects
(+30 rejected), all from the provisional pool (-60 provisional). Expected
post-batch13: provisional 51,432-60=51,372; already_covered 7,167+30=7,197;
rejected 1,550+30=1,580; confirmed_gap/merged/deferred unchanged 3/1/1.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PRE = Path("/home/z/my-project/scratch/disc002-s13-batch12.jsonl")
POST = Path("/home/z/my-project/scratch/disc002-s13-batch13.jsonl")
DECISIONS = Path(
    "/home/z/my-project/obsidian-vault-unification-docs/state/concept-candidates/002-disc002-decisions-batch13.jsonl"
)


def load(path: Path) -> dict[str, dict]:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                out[rec["candidate_id"]] = rec
    return out


def main() -> int:
    pre = load(PRE)
    post = load(POST)
    decisions = {
        json.loads(line)["candidate_id"]: json.loads(line)
        for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert set(pre) == set(post), "candidate id sets differ"
    assert len(post) == 60154, f"record count {len(post)} != 60154"

    changed = []
    unchanged_other = 0
    history_appended = 0
    mismatches = []
    for cid, rec_pre in pre.items():
        rec_post = post[cid]
        action = decisions.get(cid, {}).get("action")
        if rec_pre == rec_post:
            if action is not None:
                mismatches.append(f"{cid}: decision exists but record unchanged")
            else:
                unchanged_other += 1
            continue
        changed.append(cid)
        expected_status = (
            "already_covered" if action == "cover" else
            "rejected" if action == "reject" else None
        )
        if rec_post["status"] != expected_status:
            mismatches.append(
                f"{cid}: action={action} but status "
                f"{rec_pre['status']}->{rec_post['status']}"
            )
        pre_hist = rec_pre.get("decision_history", [])
        post_hist = rec_post.get("decision_history", [])
        if len(post_hist) == len(pre_hist) + 1 and post_hist[:-1] == pre_hist:
            history_appended += 1
        else:
            mismatches.append(f"{cid}: decision_history not cleanly appended")

    status_counts = Counter(r["status"] for r in post.values())
    expected_counts = {
        "provisional_candidate": 51372,
        "already_covered": 7197,
        "rejected": 1580,
        "confirmed_gap": 3,
        "merged": 1,
        "deferred": 1,
    }

    report = {
        "records_total": len(post),
        "records_changed": len(changed),
        "records_unchanged_no_decision": unchanged_other,
        "history_appended_cleanly": history_appended,
        "changes_by_action": dict(Counter(decisions[c]["action"] for c in changed)),
        "status_transition_check": dict(Counter(
            f"{pre[c]['status']}->{post[c]['status']}" for c in changed
        )),
        "mismatches": mismatches,
        "final_status_counts": dict(status_counts),
        "expected_status_counts": expected_counts,
        "counts_match_expectation": dict(status_counts) == expected_counts,
    }
    out = Path("/home/z/my-project/scratch/disc002-batch13-delta.json")
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))

    ok = (
        len(changed) == 60
        and not mismatches
        and history_appended == 60
        and unchanged_other == 60094
        and dict(status_counts) == expected_counts
    )
    print("DELTA VERIFICATION:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
