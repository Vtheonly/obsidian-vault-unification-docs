#!/usr/bin/env python3
"""DISC-002 merge reconciliation: rewrite the session-1 review batch (batch1)
into a replay-compatible batch2 for the MERGED decision chain.

The parallel session (commits 3d2ff8b..e2914e9, on origin/main first) applied
decisions r1 (1,153 class-based rejects) and r2 (44 individual decisions)
before this session's batch. Reconciliation rules:

- 69 candidates not touched by r1/r2: keep my decisions verbatim.
- 12 their-reject vs my-evidence-cited-cover: keep my cover. The transition
  table now allows cover from rejected (auditable reversal; my rationales
  cite file:line definitional treatments their class-based pass lacked).
- 3 their-defer vs my-cover: keep my cover (same reversal path; my evidence
  is concrete, their deferral was procedural family-mapping).
- 2 their-confirm_gap vs my-cover (second moment, bradley-terry): convert my
  decision to `revise` — the confirmed_gap stands (conservative: a dedicated
  treatment can only improve the vault), and my coverage evidence is
  recorded in the history so the synthesis planner knows treatments exist
  and the gap is in coherent DERIVATION, not total absence.
- 28 agreements (23 reject/reject + 5 cover/cover): drop as redundant —
  replaying them from terminal statuses would be invalid.

Writes state/concept-candidates/002-disc002-decisions-batch2.jsonl.
"""
from __future__ import annotations

import json
from pathlib import Path

BATCH1 = Path("state/concept-candidates/002-disc002-decisions-batch1.jsonl")
R1 = Path("state/concept-candidates/002a-disc002-decisions-r1.jsonl")
R2 = Path("state/concept-candidates/002b-disc002-decisions-r2.jsonl")
OUT = Path("state/concept-candidates/002-disc002-decisions-batch2.jsonl")
REVIEWER = "GLM-5.3 orchestrator, DISC-002 session 2026-10-28 (merge reconciliation)"


def load(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    mine = load(BATCH1)
    theirs = {d["candidate_id"]: d for d in load(R1) + load(R2)}

    kept, dropped, revised, conflicts = [], 0, 0, {}
    for d in mine:
        cid = d["candidate_id"]
        if cid not in theirs:
            kept.append(d)
            continue
        td = theirs[cid]
        if d["action"] == td["action"]:
            dropped += 1  # redundant agreement
            continue
        if td["action"] == "reject" and d["action"] == "cover":
            kept.append(d)  # evidence-cited reversal
        elif td["action"] == "defer" and d["action"] == "cover":
            kept.append(d)  # evidence-cited supersession
        elif td["action"] == "confirm_gap" and d["action"] == "cover":
            revised += 1
            kept.append(
                {
                    **d,
                    "action": "revise",
                    "rationale": (
                        "MERGE RECONCILIATION (parallel sessions disagreed; "
                        "the earlier confirm_gap stands as the conservative "
                        "disposition and this revise records the coverage "
                        "evidence for the synthesis planner): "
                        + d["rationale"]
                        + " The residual gap is therefore in a coherent "
                        "dedicated DERIVATION treatment, not total absence of "
                        "definition; the confirmed-gap note should "
                        "consolidate the fragmented treatments."
                    ),
                }
            )
        else:
            conflicts[cid] = (td["action"], d["action"])

    if conflicts:
        print("UNRESOLVED CONFLICTS:", conflicts)
        return 1

    # renumber decision ids deterministically
    for i, d in enumerate(kept, start=1):
        d["decision_id"] = f"D-DISC002-B2-{i:04d}"
        d["reviewer"] = REVIEWER

    OUT.write_text(
        "".join(json.dumps(d, sort_keys=True) + "\n" for d in kept),
        encoding="utf-8",
    )
    from collections import Counter

    print(
        f"wrote {len(kept)} decisions -> {OUT}; "
        f"dropped-as-redundant={dropped} revise-converted={revised}"
    )
    print("by action:", dict(Counter(d["action"] for d in kept)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
