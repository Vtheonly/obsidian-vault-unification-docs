#!/usr/bin/env python3
"""DISC-002 session 13 (batch 13): persist task-queue and current-state."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"

QUEUE_NOTES = (
    "DISC-002 IN PROGRESS - session 13 (2026-10-31). Baseline independently "
    "re-verified at session start: clean tree with HEAD == origin/main == "
    "c8fcfb8; 663/663 tests (reports/discovery/disc002-session13-baseline-"
    "pytest.json; NOTE: the first run in this fresh sandbox failed 662/663 "
    "because the package was not installed — the subprocess CLI test "
    "requires the documented editable install 'python3 -m pip install -e .' "
    "(FRAMEWORK_SETUP.md style 2); after install, 663/663); both vaults "
    "byte-identical to committed manifests at session start (reports/"
    "discovery/disc002-session13-manifest-{ai-course,master-ai}.json; 0 "
    "added/removed/changed). ADR-0010 replay extended to THIRTEEN decide "
    "rounds via scripts/disc002_batch13_replay.py (r1+r2+batch2..batch12 "
    "replayed with recorded --decided-utc values, then discovery-index) — "
    "CONTENT-IDENTICAL to the committed index (60,154 records; status "
    "counts matched exactly: 51,432/7,167/1,550/3/1/1; validate green; "
    "F-0019 heeded; replay ran clean on the first try; post-batch12 chain "
    "state preserved at scratch/disc002-s13-batch12.jsonl). NO NEW TOOLING "
    "DEFECTS. Reused the fence-aware batch-10/11/12 probe/verify pattern "
    "unchanged. BATCH 13 REVIEW TRANCHE: 60 highest-signal unreviewed "
    "provisional candidates (4,454 matching the signal rule of 51,432 "
    "unreviewed — exactly the session-12 handoff prediction; scripts/"
    "disc002_batch13_tranche.py, repo-relative, CAND at scratch/"
    "disc002-s13-batch12.jsonl). Tranche character: mixed — generic "
    "fragments and artifacts (code-comment/argument-label fragments "
    "'predicted labels', verb phrases 'initialize'/'model uses'/'acts "
    "like'/'use hybrid'/'use cases', numeric/LaTeX artifacts 'times 64'/"
    "'times 224'/'times 16'/'lfloor'/'rfloor'/'cos'/'sin', prose fragments "
    "'reward model needed'/'positive inputs'/'input tokens'/'later "
    "layers'/'small learning'/'small learning rate'/'ascent'/'large "
    "model'/'new data'/'loss decreases'/'across positions', example "
    "strings 'cat sat'/'emails'/'creative writing', path/vault-meta "
    "artifacts 'my-project'/'source files') plus a strong technical "
    "majority (openhermes, outside function, resnet18, scalar bias, "
    "single artificial (neuron), still sota, tree shape, true negatives, "
    "def, super, normalization layers, odot, low frequencies, feed-forward "
    "network, image features, learning rate schedules, rate schedules, "
    "goodfellow, high bias, single attention, dynamic range, latent "
    "vector, projection layer, squared gradients, steepest ascent, "
    "gradient direction, tensor shape, per filter, runtimeerror). Method: "
    "individual evidence review of all 60 brief blocks + FENCE-AWARE "
    "definitional-treatment coverage probe (scripts/disc002_batch13_probe."
    "py, ~230 terms, scratch/disc002-batch13-probe.json) + 160-check "
    "targeted citation verification (scripts/disc002_batch13_verify.py, "
    "all OK after pattern fixes for heading-number prefixes, bold-marker "
    "placement, unicode-x vs \\times regex escaping (in regex \\t means "
    "TAB) and LaTeX-command escaping) + independent subagent cross-check "
    "of ALL 60 judgment calls: 60/60 first-pass AGREE (first fully-"
    "agreeing tranche since the discipline began). Two subagent errata "
    "flagged and INDEPENDENTLY RE-VERIFIED: ACCEPTED the predicted-label "
    "symbol gloss 'ŷ is the predicted label' at master-ai '01 - "
    "Perceptrons and MLPs.md:63' (defines the symbol, not the phrase; "
    "reject stands, rationale strengthened); REJECTED the claimed "
    "latent-representation locator ':14' (direct inspection + regex "
    "verify both place it at ':15'; original citation stands). FIFTH "
    "consecutive session where subagent-erratum re-verification was "
    "required and it cut both ways. Decisions: 30 evidence-cited covers + "
    "30 noise rejects + 0 new gaps + 0 merges + 0 defers applied (--"
    "decided-utc 2026-10-31T13:30:00Z; state/concept-candidates/"
    "002-disc002-decisions-batch13.jsonl, D-DISC002-B13-0001..0060; "
    "reports/discovery/disc002-decide-batch13.json, disc002-validate-"
    "batch13.json 60,154 records 0 errors, disc002-index-batch13.json). "
    "NO NEW CONFIRMED GAP: 'still sota' resolved via the master-ai "
    "glossary SOTA entry ('28 - Glossary/Acronyms/Acronyms Index.md:177', "
    "batch-11 ddpm precedent); 'runtimeerror' resolved via the dedicated "
    "'8. Error Handling and Exception Management' note + in-situ PyTorch "
    "cause/fix diagnostics (the async def zero-treatment standard is NOT "
    "met); 'def'/'super' via the dedicated Functions/OOP notes; "
    "'lfloor'/'rfloor'/'cos'/'sin' rejected as LaTeX artifacts with "
    "covered concept side (floor function, cosine similarity, sinusoidal "
    "positional encoding, Fourier components). Delta verification PASS "
    "(60 changes: 30 provisional->already_covered + 30 provisional-"
    ">rejected; 60,094 unchanged; counts 51,372/7,197/1,580/3/1/1 = the "
    "pre-written arithmetic; one iteration: the first delta run failed on "
    "the script's STALE embedded expected_counts — per the session-11 "
    "lesson the expectation side was identified as wrong and patched; "
    "per-record checks were green on the first run). CURRENT: 51,372 "
    "provisional / 7,197 already_covered / 1,580 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged / "
    "1 deferred. NEXT: batch-14+ review tranches (4,394 still match the "
    "signal rule); per-domain semantic classification of the dossier-"
    "extension overlap pairs; then disposition assignment before gated "
    "synthesis."
)

records = []
with open(QUEUE, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))

for r in records:
    if r["task_id"] != "DISC-002":
        continue
    r["notes"] = QUEUE_NOTES

with open(QUEUE, "w", encoding="utf-8") as fh:
    for rec in records:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"task queue updated: {len(records)} records")

state = json.loads(STATE.read_text(encoding="utf-8"))
state["last_verified_checkpoint"] = (
    "state/checkpoints/checkpoint-2026-10-31-disc002-session13.json"
)
state["stage"] = "disc002-review-batch13-done"
disc = state["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]
disc["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch13.jsonl (60)"
)
disc["final_statuses"] = {
    "provisional_candidate": 51372,
    "already_covered": 7197,
    "rejected": 1580,
    "confirmed_gap": 3,
    "merged": 1,
    "deferred": 1,
}
disc["replay_decided_utc"]["batch13"] = "2026-10-31T13:30:00Z"
disc["sessions_merged"].append(
    "session 13: thirteen-round replay re-verification + batch-13 tranche "
    "(30 covers + 30 rejects, no new gap; subagent cross-check 60/60 "
    "first-pass AGREE, 2 errata re-verified: 1 accepted, 1 rejected)"
)
state["notes"] = (
    "DISC-002 in progress; session 13 re-verified the baseline (663/663 "
    "tests at start after the documented editable install in the fresh "
    "sandbox — the first run failed 662/663 on the subprocess CLI test "
    "without the install; both vaults byte-identical to manifests at "
    "start, HEAD == origin/main == c8fcfb8), extended the ADR-0010 "
    "replay to THIRTEEN decide rounds (content-identical to the "
    "committed index on the first try; expected 51,432/7,167/1,550/3/1/1 "
    "matched exactly), reused the fence-aware probe/verify pattern "
    "unchanged, and completed the batch-13 review tranche: 60 highest-"
    "signal unreviewed candidates (4,454 matching the signal rule — "
    "exactly the session-12 prediction), ~230-term fence-aware coverage "
    "probe + 160-check citation verification (all OK after pattern "
    "fixes: heading-number prefixes, bold-marker placement, \\times and "
    "\\cos regex escaping) + independent subagent cross-check of ALL 60 "
    "judgment calls: 60/60 first-pass AGREE — the first fully-agreeing "
    "tranche since the cross-check discipline began. Two errata flagged "
    "and independently re-verified: the predicted-label symbol gloss at "
    "master-ai '01 - Perceptrons and MLPs.md:63' ACCEPTED (reject "
    "stands; rationale strengthened) and the claimed "
    "latent-representation locator ':14' REJECTED (the definition is at "
    ":15; original citation stands) — fifth consecutive session where "
    "subagent-erratum re-verification cut both ways. Decisions: 30 "
    "evidence-cited covers + 30 noise rejects applied (--decided-utc "
    "2026-10-31T13:30:00Z), validate green, index regenerated and delta-"
    "verified PASS (60 changes: 30+30; 60,094 unchanged; counts match "
    "the pre-written arithmetic 51,432-60 / 7,167+30 / 1,550+30; one "
    "iteration on the script's stale embedded expectation, expectation "
    "side patched per the session-11 lesson, per-record checks green "
    "throughout). NO NEW CONFIRMED GAP: 'still sota' covered via the "
    "glossary SOTA entry (Acronyms Index:177; ddpm precedent); "
    "'runtimeerror' covered via the dedicated Error Handling note + "
    "PyTorch cause/fix diagnostics; 'def'/'super' via the dedicated "
    "Functions/OOP notes; 'lfloor'/'rfloor'/'cos'/'sin' rejected as "
    "LaTeX artifacts with covered concept side. CURRENT: 51,372 "
    "provisional / 7,197 already_covered / 1,580 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged "
    "/ 1 deferred. NEXT: batch-14+ review tranches (4,394 still match "
    "the signal rule); per-domain semantic classification of the "
    "dossier-extension overlap pairs; then disposition assignment "
    "before gated synthesis. SESSION-13 PUSH VERIFIED: recorded in the "
    "session-13 push-verification report and state commit."
)
STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
