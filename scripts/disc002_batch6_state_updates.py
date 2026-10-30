#!/usr/bin/env python3
"""DISC-002 session 6: update the task-queue record and current-state.json."""
from __future__ import annotations

import json
from pathlib import Path

QUEUE = Path("state/task-queue.jsonl")
STATE = Path("state/current-state.json")

lines = [l for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
records = [json.loads(l) for l in lines]

disc = None
for r in records:
    if r.get("task_id") == "DISC-002":
        disc = r
assert disc is not None and disc["status"] == "in_progress"

# 1. update notes with session-6 evidence (no new findings this session:
#    the six-round replay ran clean on the first try, validating the F-0020 fix)
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 6 (2026-10-30). Session 5 completed the batch-5 review "
    "tranche (20 covers + 40 rejects) and fixed tooling defect F-0020 (see "
    "checkpoint-2026-10-30-disc002-session5.json). Session 6 re-verified the baseline "
    "independently: 663/663 tests at session start "
    "(reports/discovery/disc002-session6-baseline-pytest.json), both vaults byte-identical "
    "to committed manifests at start (reports/discovery/disc002-session6-manifest-{ai-course,master-ai}.json). "
    "ADR-0010 replay re-verified end-to-end via scripts/disc002_batch6_replay.py (six decide "
    "rounds now: r1+r2+batch2+batch3+batch4+batch5 replayed with the recorded --decided-utc "
    "values, then discovery-index) — CONTENT-IDENTICAL to the committed index (60,154 "
    "records; status counts matched exactly: 51,852/7,001/1,298/2/1; validate green; F-0019 "
    "content-comparison heeded; the replay ran clean on the first try, validating the F-0020 "
    "regression fix). NO NEW TOOLING DEFECTS THIS SESSION. "
    "BATCH 6 REVIEW TRANCHE: 60 highest-signal unreviewed provisional candidates "
    "(4,874 matching the signal rule of 51,852 unreviewed; scripts/disc002_batch6_tranche.py, "
    "repo-relative). Tranche character: dominated by generic English vocabulary and prose "
    "fragments. Method: individual evidence review of all 60 brief blocks + "
    "definitional-treatment coverage probe (scripts/disc002_batch6_probe.py, 34 terms) + "
    "targeted citation verification (scripts/disc002_batch6_verify.py, 37 locator checks) + "
    "independent subagent cross-check of 15 judgment calls: 15/15 AGREE; corrections "
    "incorporated (ai-course chapter-level path completions; master-ai glossary diag(x) entry "
    "for the diagonal cover — the 'Tensors and Broadcasting' '# 6. Diagonal extraction' is a "
    "code comment, recharacterized; Gaussian Distribution note strengthens the randn cover). "
    "DECISIONS: 5 evidence-cited covers (randn, eval set, sklearn, probability distribution, "
    "diagonal) + 55 noise rejects "
    "(state/concept-candidates/002-disc002-decisions-batch6.jsonl; applied with "
    "--decided-utc 2026-10-30T16:30:00Z; reports/discovery/disc002-decide-batch6.json "
    "decisions_applied 1523 cumulative, disc002-validate-batch6.json 60,154 records 0 errors, "
    "disc002-index-batch6.json). No new confirmed gaps (2 remain: second moment, "
    "bradley-terry). POST-BATCH6: 51,792 provisional / 7,006 already_covered / 1,353 "
    "rejected / 2 confirmed_gap / 1 deferred; index delta-verified exactly (-60 provisional, "
    "+5 covered, +55 rejected). REMAINING: batch-7+ review tranches (~4,814 still match the "
    "signal rule); per-domain semantic classification of the 69,185 dossier-extension "
    "overlap pairs (no bulk absorption); disposition assignment (release-blocking) before "
    "gated synthesis. Review standard unchanged: individual evidence review with file:line "
    "citations, subagent cross-check, confirmed gaps RARE."
)

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (DISC-002 notes); records:", len(records))

# 2. current-state.json
st = json.loads(STATE.read_text(encoding="utf-8"))
st["stage"] = "disc002-review-batch6-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-30-disc002-session6.json"
st["notes"] = (
    "DISC-002 in progress; session 6 re-verified the baseline (663/663 tests at start, both "
    "vaults byte-identical to manifests), replayed the six-round ADR-0010 chain end-to-end "
    "(content-identical to the committed index before the batch-6 apply; replay ran clean on "
    "the first try, validating the F-0020 fix; no new tooling defects), and completed the "
    "batch-6 review tranche: 60 highest-signal unreviewed candidates (generic-vocabulary-"
    "dominated tranche), 34-term coverage probe + targeted citation verification + "
    "independent subagent cross-check (15 judgment calls, 15/15 AGREE, path completions and "
    "two evidence upgrades incorporated). Decisions: 5 evidence-cited covers (randn, eval "
    "set, sklearn, probability distribution, diagonal) + 55 noise rejects applied "
    "(--decided-utc 2026-10-30T16:30:00Z), validate green, index regenerated and "
    "delta-verified. No new confirmed gaps (2 remain: second moment, bradley-terry). "
    "CURRENT: 51792 provisional / 7006 already_covered / 1353 rejected / 2 confirmed_gap / "
    "1 deferred (ssd framework). NEXT: batch-7+ review tranches (~4,814 still match the "
    "signal rule); per-domain semantic classification of the dossier-extension overlap "
    "pairs (no bulk absorption); then disposition assignment before gated synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7006,
    "confirmed_gap": 2,
    "deferred": 1,
    "provisional_candidate": 51792,
    "rejected": 1353,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch6.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch6"] = (
    "2026-10-30T16:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 6: six-round replay re-verification + batch-6 tranche"
)
STATE.write_text(json.dumps(st, indent=1, sort_keys=False) + "\n", encoding="utf-8")
print("current-state.json updated (stage disc002-review-batch6-done)")
