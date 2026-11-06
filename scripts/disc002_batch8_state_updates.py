#!/usr/bin/env python3
"""DISC-002 session 8: update the task-queue record and current-state.json."""
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

# 1. update notes with session-8 evidence (no new tooling defects this session)
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 8 (2026-10-31). Session 7 completed the batch-7 review "
    "tranche (15 covers + 1 confirmed gap async def + 1 merge + 43 rejects). Session 8 "
    "re-verified the baseline independently: 663/663 tests at session start "
    "(reports/discovery/disc002-session8-baseline-pytest.json), both vaults byte-identical "
    "to committed manifests at session start (reports/discovery/disc002-session8-manifest-"
    "{ai-course,master-ai}.json; 0 added/removed/changed; git HEAD == origin/main == 4e25398, "
    "clean tree). ADR-0010 replay extended to EIGHT decide rounds via "
    "scripts/disc002_batch8_replay.py (r1+r2+batch2..batch7 replayed with the recorded "
    "--decided-utc values, then discovery-index) — CONTENT-IDENTICAL to the committed index "
    "(60,154 records; status counts matched exactly: 51,732/7,021/1,396/3/1/1; validate "
    "green; F-0019 content-comparison heeded; replay ran clean on the first try; post-batch7 "
    "chain state preserved at scratch/disc002-s8-batch7.jsonl). NO NEW TOOLING DEFECTS THIS "
    "SESSION. BATCH 8 REVIEW TRANCHE: 60 highest-signal unreviewed provisional candidates "
    "(4,754 matching the signal rule of 51,732 unreviewed; scripts/disc002_batch8_tranche.py, "
    "repo-relative, reads the replayed post-batch7 state). Tranche character: mixed — heavy "
    "generic English vocabulary (gerunds, adverbs, participles, a mermaid fill-color artifact "
    "'e1f5fe', a LaTeX \\operatorname artifact, a date '2026-08-08', a numeric range '2-5') "
    "plus a technical minority (MCP overview, reasoning capability, chapter-title fragments "
    "13-inference/10-model-architecture/agent-vs-workflow family, PPO deep treatment, "
    "test data, BERT-family, computation graph, float32, partial derivative, typing, "
    "augmentations, conv layers, InstructGPT 2022, SiLU, channel depth, embedder, unfrozen, "
    "bilinear, draft head, output validation, predicted class). Method: individual evidence "
    "review of all 60 brief blocks + definitional-treatment coverage probe "
    "(scripts/disc002_batch8_probe.py, 86 terms) + targeted citation verification "
    "(scripts/disc002_batch8_verify.py, 67 locator checks, all OK after 4 pattern fixes: "
    "agent-vs-workflow real title line 7, retain_graph 'for re-use' wording, "
    "vanishing/exploding '# 15.' prefix, batch-norm '# 16.' prefix) + independent subagent "
    "cross-check of 28 judgment calls (16 covers + 12 borderline rejects): 28/28 AGREE; "
    "corrections incorporated (unfrozen citation :210 not :212; bert-family leap :109 not "
    ":110; chapter 13 = MOC + 7 notes not 8; chapter 10 = 16 model notes + MOC + 2026 "
    "Synthesis not 13; float32 prose anchor :427 preferred over the :310 code comment; SiLU "
    "definition rests on Activation Functions.md:97 + Perceptrons/MLPs.md:206 — the FFN Deep "
    "SwiGLU heading :51 does not mention SiLU). DECISIONS: 29 evidence-cited covers + 0 "
    "confirm_gap + 0 merge + 31 noise rejects (state/concept-candidates/002-disc002-"
    "decisions-batch8.jsonl; applied with --decided-utc 2026-10-31T01:30:00Z; reports/"
    "discovery/disc002-decide-batch8.json decisions_applied 1644 cumulative, "
    "disc002-validate-batch8.json 60,154 records 0 errors, disc002-index-batch8.json). "
    "POST-BATCH8: 51,672 provisional / 7,050 already_covered / 1,427 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged / 1 deferred; "
    "index delta-verified exactly (-60 provisional, +29 covered, +31 rejected; confirmed_gap/"
    "merged/deferred unchanged). NO NEW CONFIRMED GAP this tranche: the three gap-shaped "
    "candidates all have real definitional treatments (typing: dynamic typing defined in "
    "ai-course '02.2/01' ## 1.1 + type hints in-situ via PydanticAI:11/Semantic-Kernel:229, "
    "static typing zero corpus-wide but core concept IS defined; computation graph: "
    "dedicated sections in BOTH vaults; bilinear: dedicated interpolation note with "
    "### Bilinear/Bicubic/Nearest-neighbor headings). Incidental subagent notes for future "
    "tranches: autograd anchors exist at 04.2/04:197 + chapter-summary :202; GEGLU headings "
    "at Activation Functions.md:107 + FFN Deep.md:60; 'bilinear' algebraic sense in-situ at "
    "Dot Product.md:93; GOSS defined in-situ at 03.7/03:95; right-to-explanation in-situ at "
    "Black Box.md:22 + PII.md:165. REMAINING: batch-9+ review tranches (~4,694 still match "
    "the signal rule); per-domain semantic classification of the 69,185 dossier-extension "
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
st["stage"] = "disc002-review-batch8-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-31-disc002-session8.json"
st["notes"] = (
    "DISC-002 in progress; session 8 re-verified the baseline (663/663 tests at start, both "
    "vaults byte-identical to manifests at start; git HEAD == origin/main == 4e25398 clean), "
    "extended the ADR-0010 replay to eight decide rounds (content-identical to the committed "
    "index; replay ran clean on the first try; no new tooling defects), and completed the "
    "batch-8 review tranche: 60 highest-signal unreviewed candidates (mixed generic + "
    "technical tranche), 86-term coverage probe + 67-check citation verification + "
    "independent subagent cross-check (28 judgment calls, 28/28 AGREE, corrections "
    "incorporated: unfrozen line, bert-family line, chapter-13/10 note counts, float32 "
    "prose anchor, SiLU definition location). Decisions: 29 evidence-cited covers + 0 new "
    "gaps + 0 merges + 31 noise rejects applied (--decided-utc 2026-10-31T01:30:00Z), "
    "validate green, index regenerated and delta-verified. The three gap-shaped candidates "
    "(typing, computation graph, bilinear) all have real definitional treatments — no new "
    "confirmed gap. CURRENT: 51,672 provisional / 7,050 already_covered / 1,427 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: "
    "batch-9+ review tranches (~4,694 still match the signal rule); per-domain semantic "
    "classification of the dossier-extension overlap pairs; then disposition assignment "
    "before gated synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7050,
    "confirmed_gap": 3,
    "deferred": 1,
    "merged": 1,
    "provisional_candidate": 51672,
    "rejected": 1427,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch8.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch8"] = (
    "2026-10-31T01:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 8: eight-round replay re-verification + batch-8 tranche (29 covers + 31 "
    "rejects, no new gap)"
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
