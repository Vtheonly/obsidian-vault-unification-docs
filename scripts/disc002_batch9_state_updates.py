#!/usr/bin/env python3
"""DISC-002 session 9: update the task-queue record and current-state.json."""
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

# 1. update notes with session-9 evidence (no new tooling defects this session;
#    one recurring documentation-level defect class caught again: probe heading
#    hits matching '#' comments inside code fences — see fence note below)
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 9 (2026-10-31). FIRST ACTION: resolved the session-8 "
    "push blocker — the user re-supplied the PAT, commits 6171b4f (work) + 24206dd (state) "
    "were pushed (4e25398..24206dd) and reports/discovery/disc002-session8-push-"
    "verification.json recorded in state commit 54dcc4b (verified HEAD == origin/main == "
    "54dcc4b). Session 9 then re-verified the baseline independently: 663/663 tests at "
    "session start (reports/discovery/disc002-session9-baseline-pytest.json), both vaults "
    "byte-identical to committed manifests at session start (reports/discovery/"
    "disc002-session9-manifest-{ai-course,master-ai}.json; 0 added/removed/changed). "
    "ADR-0010 replay extended to NINE decide rounds via scripts/disc002_batch9_replay.py "
    "(r1+r2+batch2..batch8 replayed with the recorded --decided-utc values, then "
    "discovery-index) — CONTENT-IDENTICAL to the committed index (60,154 records; status "
    "counts matched exactly: 51,672/7,050/1,427/3/1/1; validate green; F-0019 "
    "content-comparison heeded; replay ran clean on the first try; post-batch8 chain state "
    "preserved at scratch/disc002-s9-batch8.jsonl). NO NEW TOOLING DEFECTS THIS SESSION. "
    "BATCH 9 REVIEW TRANCHE: 60 highest-signal unreviewed provisional candidates (4,694 "
    "matching the signal rule of 51,672 unreviewed — exactly the count the session-8 "
    "handoff predicted; scripts/disc002_batch9_tranche.py, repo-relative, reads the "
    "replayed post-batch8 state). Tranche character: mixed — generic English vocabulary "
    "(adverbs 'globally'/'arbitrarily', gerunds/participles 'demonstrating'/'compressing'/"
    "'substituting'/'transformed', nouns 'lesson'/'records'/'degrees'/'cameras'/'command', "
    "possessive \"tool's\"), markup/code artifacts (\"default'\" 'DEFAULT' string, \"pth'\" "
    "'.pth', 'bn1'/'bn2' BatchNorm2d attribute names, 'gen' multi-sense fragment, '100x', "
    "'network module'/'neural network module' import comments, README-only taxonomy "
    "labels 'academic dl'/'academic ml') plus a strong technical minority (dropout rate, "
    "exploding gradient problem, attention layer, additive attention, previous-token, "
    "value function, preference pairs, DPO family, RAG, tokens per parameter, utf-8, "
    "pointwise, stride-2, main path, convolutional base, ReLU activations, open-weights "
    "LLM, agent-lifecycle and agent-vs-workflow title fragments, BERT 2018 / "
    "Constitutional AI 2022 paper fragments, chapter fragments '12 fine-tuning' and "
    "'chapter 07'). Method: individual evidence review of all 60 brief blocks + "
    "definitional-treatment coverage probe (scripts/disc002_batch9_probe.py, 82 terms) + "
    "targeted citation verification (scripts/disc002_batch9_verify.py, 139 locator "
    "checks, all OK after 4 pattern fixes: mobilenet 'Pointwise convolution (1×1)' "
    "unicode ×, 1x1-note real heading — the probe's '# 1x1 convolution' hit was a Python "
    "comment in a fence at :312 while the real heading is '## 1×1 Convolutions: Why They "
    "Seem Useless' :223 (recurring fence class, third session in a row), strides-note "
    "real title '# 2.3 Strides', import-comment path 03.2/08) + independent subagent "
    "cross-check of 28 judgment calls: 28/28 AGREE. Subagent corrections INDEPENDENTLY "
    "RE-VERIFIED before incorporation (two were themselves wrong and rejected): VERIFIED "
    "and incorporated — SSO usage is 18 word-boundary occurrences across 3 notes (incl. "
    "MCP Marketplace :372; the original '3x in 2 notes' framing came from the candidate's "
    "evidence quotes only), Data Prep 'determines model capacity' is :174 not :175, "
    "BatchNorm running_mean comment is :192 not :194, BPE.md:261 is a real in-situ UTF-8 "
    "definition, 04.3/04:15 is a direct definitional treatment of 'representational "
    "capacity', the Lifecycles note's aliases include 'Agent Lifecycles' :6, real "
    "attention-layer headings exist (Kimi Linear '### Full Attention Layers' :62, "
    "Flamingo '### 4. Gated Cross-Attention Layers' :61). REJECTED as wrong — the "
    "AI-vs-ML wikilink IS at :292 (subagent claimed :293) and the LaTeX gen cluster DOES "
    "exist as \\mathcal{L}_{\\text{gen}} at '05. Normalization, Regularization and "
    "Augmentation - Summary.md:14' (the subagent searched without the \\text{} wrapper). "
    "DECISIONS: 35 evidence-cited covers + 0 confirm_gap + 0 merge + 25 noise rejects "
    "(state/concept-candidates/002-disc002-decisions-batch9.jsonl; applied with "
    "--decided-utc 2026-10-31T03:00:00Z; reports/discovery/disc002-decide-batch9.json "
    "decisions_applied 1704 cumulative, disc002-validate-batch9.json 60,154 records 0 "
    "errors, disc002-index-batch9.json). POST-BATCH9: 51,612 provisional / 7,085 "
    "already_covered / 1,452 rejected / 3 confirmed_gap (second moment, bradley-terry, "
    "async def) / 1 merged / 1 deferred; index delta-verified exactly (-60 provisional, "
    "+35 covered, +25 rejected; all 60 statuses correct; all other 60,094 records "
    "unchanged including ku_ids; confirmed_gap/merged/deferred unchanged). NO NEW "
    "CONFIRMED GAP this tranche: the gap-shaped candidates all resolved — "
    "representational capacity has a DIRECT definitional treatment at 04.3/04:15; utf-8 "
    "has a real in-situ definition at BPE.md:261; sso is a peripheral enterprise "
    "integration term (18 occurrences/3 notes) whose identity/auth role is explained "
    "in-situ at every use site and is not load-bearing for any derivation — adjudicated "
    "reject, not gap (subagent agreed). NEW PRECEDENT RECORDED for the cover/reject "
    "boundary: 'pth'' = cover because the underlying state_dict concept has DEDICATED "
    "definitional sections (## 7. model.state_dict() :543 + ### 7.1 :545); \"default'\" = "
    "reject because weights='DEFAULT' has only in-situ code-comment explanations — "
    "dedicated section vs in-situ comment is the line. REMAINING: batch-10+ review "
    "tranches (~4,634 still match the signal rule); per-domain semantic classification "
    "of the 69,185 dossier-extension overlap pairs (no bulk absorption); disposition "
    "assignment (release-blocking) before gated synthesis. Review standard unchanged: "
    "individual evidence review with file:line citations, subagent cross-check with "
    "independent re-verification of subagent corrections, confirmed gaps RARE."
)

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (DISC-002 notes); records:", len(records))

# 2. current-state.json
st = json.loads(STATE.read_text(encoding="utf-8"))
st["stage"] = "disc002-review-batch9-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-31-disc002-session9.json"
st["notes"] = (
    "DISC-002 in progress; session 9 first resolved the session-8 push blocker (PAT "
    "re-supplied; 6171b4f + 24206dd pushed as 4e25398..24206dd and verified; push "
    "verification recorded in 54dcc4b), then re-verified the baseline (663/663 tests at "
    "start, both vaults byte-identical to manifests), extended the ADR-0010 replay to "
    "nine decide rounds (content-identical to the committed index; replay ran clean on "
    "the first try; no new tooling defects), and completed the batch-9 review tranche: 60 "
    "highest-signal unreviewed candidates (mixed generic + technical tranche), 82-term "
    "coverage probe + 139-check citation verification + independent subagent cross-check "
    "of 28 judgment calls (28/28 AGREE; subagent corrections independently re-verified — "
    "two were wrong and rejected). Decisions: 35 evidence-cited covers + 0 new gaps + 0 "
    "merges + 25 noise rejects applied (--decided-utc 2026-10-31T03:00:00Z), validate "
    "green, index regenerated and delta-verified. The three gap-shaped candidates "
    "(representational capacity, utf-8, sso) all resolved with real definitional "
    "treatments or in-situ role explanations — no new confirmed gap. CURRENT: 51,612 "
    "provisional / 7,085 already_covered / 1,452 rejected / 3 confirmed_gap (second "
    "moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: batch-10+ review "
    "tranches (~4,634 still match the signal rule); per-domain semantic classification "
    "of the dossier-extension overlap pairs; then disposition assignment before gated "
    "synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7085,
    "confirmed_gap": 3,
    "deferred": 1,
    "merged": 1,
    "provisional_candidate": 51612,
    "rejected": 1452,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch9.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch9"] = (
    "2026-10-31T03:00:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 9: session-8 push blocker resolved + nine-round replay re-verification + "
    "batch-9 tranche (35 covers + 25 rejects, no new gap)"
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
