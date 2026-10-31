#!/usr/bin/env python3
"""DISC-002 session 12 (batch 12): persist task-queue and current-state."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"

records = []
with open(QUEUE, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))

for r in records:
    if r["task_id"] != "DISC-002":
        continue
    r["notes"] = (
        "DISC-002 IN PROGRESS - session 12 (2026-10-31). Baseline independently "
        "re-verified at session start: clean tree with HEAD == origin/main == "
        "6d1cf8e; 663/663 tests (reports/discovery/disc002-session12-baseline-"
        "pytest.json); both vaults byte-identical to committed manifests at "
        "session start (reports/discovery/disc002-session12-manifest"
        "-{ai-course,master-ai}.json; 0 added/removed/changed). ADR-0010 "
        "replay extended to TWELVE decide rounds via scripts/"
        "disc002_batch12_replay.py (r1+r2+batch2..batch11 replayed with recorded "
        "--decided-utc values, then discovery-index) — CONTENT-IDENTICAL to the "
        "committed index (60,154 records; status counts matched exactly: "
        "51,492/7,142/1,515/3/1/1; validate green; F-0019 heeded; replay ran "
        "clean on the first try; post-batch11 chain state preserved at scratch/"
        "disc002-s12-batch11.jsonl). NO NEW TOOLING DEFECTS. Reused the "
        "fence-aware batch-10/11 probe/verify pattern unchanged. BATCH 12 "
        "REVIEW TRANCHE: 60 highest-signal unreviewed provisional candidates "
        "(4,514 matching the signal rule of 51,492 unreviewed — exactly the "
        "session-11 handoff prediction; scripts/disc002_batch12_tranche.py, "
        "repo-relative). Tranche character: mixed — generic fragments and code "
        "artifacts (path/key/variable fragments \"train'\"/\"val'\"/\"epoch'\"/"
        "'val acc'/'train acc'/'best validation accuracy'/'epoch summary', "
        "code-comment phrases 'core pytorch (library)'/'move data'/'move "
        "images'/'move labels'/'model parameters using'/'gradients via "
        "(backpropagation)', verb phrases 'randomly crop'/'filter slides "
        "across'/'max pooling selects'/'model verifies'/'answer directly'/"
        "'networks deeper', prompt-string artifacts 'let's think (step)', "
        "possessives \"colpali's\"/\"network's guess\", numeric fragments "
        "'10x larger'/'1b-parameter model'/'1000 imagenet (classes)', vault "
        "navigation label 'fine-tuning moc', worked-example class artifact "
        "'mnistnet', locative adjective 'server-side', prose fragments "
        "'entire training dataset'/'multiple approaches'/'gradients via') "
        "plus a strong technical minority (class label(s), convolutional "
        "block, cot chains, fully-connected layer, logsoftmax, (reward) "
        "models 2023, single fixed-length vector, sparse signal, avg pool, "
        "class scores, final relu, imagenet weights, input spatial size, "
        "output error, uses running stats, grad-cam heatmap, pre-trained "
        "resnet-50, sgd optimizer, cifar10, inside function, "
        "late-interaction retrieval, multi-class problems). Method: "
        "individual evidence review of all 60 brief blocks + FENCE-AWARE "
        "definitional-treatment coverage probe (scripts/"
        "disc002_batch12_probe.py, 137 terms) + targeted citation "
        "verification (scripts/disc002_batch12_verify.py, 154 locator checks, "
        "all OK after 5 exact-text pattern fixes — heading-form, **bold**-"
        "marker, missing-word, heading-level and note-title-vs-filename "
        "classes) + independent subagent cross-check of ALL 60 judgment "
        "calls: 59/60 first-pass AGREE. THE ONE DISAGREEMENT (cifar10) was "
        "INDEPENDENTLY RE-VERIFIED by the orchestrator and the SUBAGENT WAS "
        "RIGHT — a TERM-SEPARATED CIFAR-10 definition exists in the Q11 quiz "
        "matching block ('c) CIFAR-10 dataset' :178 paired with 'n) A "
        "popular benchmark dataset for deep learning with 60,000 32x32 color "
        "images in 10 classes' :182, answer key 'c) -> n)' :190); the "
        "definition line does NOT contain the string 'CIFAR', so term-only "
        "grep missed it; the orchestrator's draft confirm_gap was CORRECTED "
        "to cover before applying. FOURTH consecutive session with a "
        "decisive subagent correction; the re-verification step stays "
        "mandatory. Other errata accepted after re-verification: LogSoftmax "
        ":109 belongs to '08. Loss Functions and Optimizers Deep Dive.md' "
        "(not '02. Loss Functions and Cost Optimization.md'); thought-vector "
        "def at 'Origins of Attention.md:19' (not the Bahdanau 2014 note); "
        "heading-level fixes (### not ##) for running-stats/SGD/"
        "late-interaction headings. DECISIONS: 25 evidence-cited covers + 0 "
        "confirm_gap + 0 merge + 35 noise rejects (state/concept-candidates/"
        "002-disc002-decisions-batch12.jsonl; applied with --decided-utc "
        "2026-10-31T10:30:00Z — chain-consistent value after batch-11's "
        "08:00:00Z; reports/discovery/disc002-decide-batch12.json, "
        "disc002-validate-batch12.json 60,154 records 0 errors, "
        "disc002-index-batch12.json). POST-BATCH12: 51,432 provisional / "
        "7,167 already_covered / 1,550 rejected / 3 confirmed_gap (second "
        "moment, bradley-terry, async def) / 1 merged / 1 deferred; index "
        "delta-verified exactly (scripts/disc002_batch12_delta.py: -60 "
        "provisional, +25 covered, +35 rejected; all 60 statuses correct; "
        "all 60 decision_history entries appended; all other 60,094 records "
        "unchanged; PASS ON THE FIRST RUN — expectation arithmetic written "
        "down before running, the session-11 discipline applied). NO NEW "
        "CONFIRMED GAP. NEW PROBE LESSON RECORDED (extends the session-10 "
        "hyphenation and session-11 glossary lessons): definitions can be "
        "TERM-SEPARATED — quiz matching blocks pair a Group-A term with a "
        "Group-B definition whose line does not contain the term; before "
        "claiming definitional absence, inspect description lines near every "
        "occurrence and search property-based phrases ('60,000 32x32', '10 "
        "classes') rather than only the term. REMAINING: batch-13+ review "
        "tranches (~4,454 still match the signal rule); per-domain semantic "
        "classification of the 69,185 dossier-extension overlap pairs (no "
        "bulk absorption); disposition assignment (release-blocking) before "
        "gated synthesis. Review standard unchanged: individual evidence "
        "review with file:line citations, subagent cross-check with "
        "independent re-verification of subagent corrections (and of one's "
        "OWN gap claims — the cifar10 case), confirmed gaps RARE."
    )

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (DISC-002 notes); records:", len(records))

# 2. current-state.json
st = json.loads(STATE.read_text(encoding="utf-8"))
st["stage"] = "disc002-review-batch12-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-31-disc002-session12.json"
st["notes"] = (
    "DISC-002 in progress; session 12 re-verified the baseline (663/663 tests "
    "at start, both vaults byte-identical to manifests at start and end, HEAD "
    "== origin/main == 6d1cf8e), extended the ADR-0010 replay to TWELVE decide "
    "rounds (content-identical to the committed index; replay ran clean on "
    "the first try), reused the fence-aware probe/verify pattern unchanged, "
    "and completed the batch-12 review tranche: 60 highest-signal unreviewed "
    "candidates (mixed generic + technical tranche), 137-term fence-aware "
    "coverage probe + 154-check citation verification + independent subagent "
    "cross-check of ALL 60 judgment calls (59/60 first-pass AGREE; the ONE "
    "disagreement — cifar10 — independently re-verified and the SUBAGENT was "
    "right: a TERM-SEPARATED CIFAR-10 definition exists in the Q11 quiz "
    "matching block at :178/:182/:190; the orchestrator's draft confirm_gap "
    "was corrected to cover before applying; fourth consecutive session with "
    "a decisive subagent correction). Decisions: 25 evidence-cited covers + "
    "0 new gaps + 0 merges + 35 noise rejects applied (--decided-utc "
    "2026-10-31T10:30:00Z), validate green, index regenerated and "
    "delta-verified (PASS on the first run; expectation arithmetic written "
    "down before running). NEW PROBE LESSON: definitions can be "
    "TERM-SEPARATED (quiz matching blocks) — search property-based phrases "
    "near term occurrences before claiming definitional absence; extends the "
    "session-10 hyphenation and session-11 glossary lessons. CURRENT: 51,432 "
    "provisional / 7,167 already_covered / 1,550 rejected / 3 confirmed_gap "
    "(second moment, bradley-terry, async def) / 1 merged / 1 deferred. "
    "NEXT: batch-13+ review tranches (~4,454 still match the signal rule); "
    "per-domain semantic classification of the dossier-extension overlap "
    "pairs; then disposition assignment before gated synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7167,
    "confirmed_gap": 3,
    "deferred": 1,
    "merged": 1,
    "provisional_candidate": 51432,
    "rejected": 1550,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch12.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch12"] = (
    "2026-10-31T10:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 12: twelve-round replay re-verification + batch-12 tranche "
    "(25 covers + 35 rejects, no new gap; cifar10 gap claim corrected to "
    "cover via the term-separated Q11:182 definition)"
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
