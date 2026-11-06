#!/usr/bin/env python3
"""DISC-002 session 5: update the task-queue record and current-state.json."""
from __future__ import annotations

import json
from pathlib import Path

QUEUE = Path("state/task-queue.jsonl")
STATE = Path("state/current-state.json")

lines = [l for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
records = [json.loads(l) for l in lines]
assert len(records) == 22, f"expected 22 queue records, got {len(records)}"

disc = None
for r in records:
    if r.get("task_id") == "DISC-002":
        disc = r
assert disc is not None and disc["status"] == "in_progress"

# 1. append F-0020 to findings
if "F-0020" not in disc["findings"]:
    disc["findings"].append("F-0020")

# 2. update notes with session-5 evidence
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 5 (2026-10-30, fresh clone). Session 4 completed "
    "the batch-4 review tranche (36 covers + 24 rejects) and verified the full "
    "baseline (see checkpoint-2026-10-30-disc002-session4.json). Session 5 re-verified "
    "the baseline independently: 662/662 tests at session start "
    "(reports/discovery/disc002-session5-baseline-pytest.json), both vaults byte-identical "
    "to committed manifests at start (reports/discovery/disc002-session5-manifest-{ai-course,master-ai}.json). "
    "ADR-0010 replay re-verified end-to-end via scripts/disc002_batch5_replay.py: "
    "vu discover-gaps over all 70 recorded batches (60,154 candidates) then "
    "r1+r2+batch2+batch3+batch4 replayed with the recorded --decided-utc values, then "
    "discovery-index - CONTENT-IDENTICAL to the committed index (status counts matched "
    "exactly: 51,912/6,981/1,258/2/1; validate green; F-0019 content-comparison heeded). "
    "TOOLING DEFECT FOUND AND FIXED DURING THE REPLAY: F-0020 - `python -m "
    "vault_unification.cli` was a silent no-op (module imported, nothing executed, exit 0, "
    "no outputs) because cli.py lacked a __main__ guard; the first replay run produced zero "
    "output files while every step 'succeeded'. Fixed by adding the guard to "
    "src/vault_unification/cli.py + regression test "
    "tests/test_cli.py::test_module_cli_execution_is_not_a_silent_noop (happy path --version "
    "must print; failure path missing-file must exit 1 with an error). "
    "BATCH 5 REVIEW TRANCHE: 60 highest-signal unreviewed provisional candidates "
    "(4,934 matching the signal rule of 51,912 unreviewed; scripts/disc002_batch5_tranche.py, "
    "repo-relative). Individual evidence review + definitional-treatment coverage probe "
    "(scripts/disc002_batch5_probe.py, 41 terms) + targeted corpus verification for boundary "
    "cases (generative-model glossary entry, center-crop rationale, flat-minima treatments "
    "in both vaults, Inception branch concatenation, focal-loss/class-imbalance, omit-bias "
    "math reason, patch-representation treatments, VAE-decoder role, initialization "
    "sensitivity, BN/Dropout train-eval sections) + independent subagent cross-check of 14 "
    "judgment calls: 14/14 AGREE, 4 citation path corrections incorporated (full "
    "vault-relative paths with chapter-level parents). DECISIONS: 20 evidence-cited covers + "
    "40 noise rejects (state/concept-candidates/002-disc002-decisions-batch5.jsonl; applied "
    "with --decided-utc 2026-10-30T15:30:00Z; reports/discovery/disc002-decide-batch5.json "
    "decisions_applied 1463 cumulative, disc002-validate-batch5.json 60,154 records 0 errors, "
    "disc002-index-batch5.json). No new confirmed gaps (2 remain: second moment, "
    "bradley-terry). POST-BATCH5: 51,852 provisional / 7,001 already_covered / 1,298 "
    "rejected / 2 confirmed_gap / 1 deferred; index delta-verified exactly (-60 provisional, "
    "+20 covered, +40 rejected). REMAINING: batch-6+ review tranches (~4,874 still match the "
    "signal rule); per-domain semantic classification of the 69,185 dossier-extension "
    "overlap pairs (no bulk absorption); disposition assignment (release-blocking) before "
    "gated synthesis. Review standard unchanged: individual evidence review with file:line "
    "citations, subagent cross-check, confirmed gaps RARE."
)

# 3. record the session-5 test runs (final run happens after this update; recorded below)
QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (DISC-002 notes + F-0020); records:", len(records))

# 4. current-state.json
st = json.loads(STATE.read_text(encoding="utf-8"))
st["stage"] = "disc002-review-batch5-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-30-disc002-session5.json"
st["notes"] = (
    "DISC-002 in progress; session 5 (fresh clone) verified the full baseline "
    "(662/662 tests at start, both vaults byte-identical to manifests), replayed the "
    "ADR-0010 chain end-to-end (content-identical to the committed index before the "
    "batch-5 apply), found+fixed+regression-tested tooling defect F-0020 (silent no-op "
    "`python -m vault_unification.cli`), and completed the batch-5 review tranche: 60 "
    "highest-signal unreviewed candidates, 51-term coverage probe + targeted corpus "
    "verification + independent subagent cross-check (14 judgment calls, 14/14 AGREE, 4 "
    "citation corrections incorporated). Decisions: 20 evidence-cited covers + 40 noise "
    "rejects applied (--decided-utc 2026-10-30T15:30:00Z), validate green, index "
    "regenerated and delta-verified. No new confirmed gaps (2 remain: second moment, "
    "bradley-terry). CURRENT: 51852 provisional / 7001 already_covered / 1298 rejected / "
    "2 confirmed_gap / 1 deferred (ssd framework). NEXT: batch-6+ review tranches (~4,874 "
    "still match the signal rule); per-domain semantic classification of the "
    "dossier-extension overlap pairs (no bulk absorption); then disposition assignment "
    "before gated synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7001,
    "confirmed_gap": 2,
    "deferred": 1,
    "provisional_candidate": 51852,
    "rejected": 1298,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch5.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch5"] = (
    "2026-10-30T15:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 5: fresh-clone verification + F-0020 fix + batch-5 tranche"
)
STATE.write_text(json.dumps(st, indent=1, sort_keys=False) + "\n", encoding="utf-8")
print("current-state.json updated (stage disc002-review-batch5-done)")
