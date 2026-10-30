#!/usr/bin/env python3
"""DISC-002 session 7: update the task-queue record and current-state.json."""
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

# 1. update notes with session-7 evidence (no new tooling defects this session)
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 7 (2026-10-31). Session 6 completed the batch-6 review "
    "tranche (5 covers + 55 rejects) and re-verified the six-round ADR-0010 chain "
    "(checkpoint-2026-10-30-disc002-session6.json). Session 7 re-verified the baseline "
    "independently: 663/663 tests at session start "
    "(reports/discovery/disc002-session7-baseline-pytest.json), both vaults byte-identical "
    "to committed manifests at start (reports/discovery/disc002-session7-manifest-{ai-course,master-ai}.json) "
    "and again at session end (-end- reports). ADR-0010 replay extended to SEVEN decide "
    "rounds via scripts/disc002_batch7_replay.py (r1+r2+batch2..batch6 replayed with the "
    "recorded --decided-utc values, then discovery-index) — CONTENT-IDENTICAL to the "
    "committed index (60,154 records; status counts matched exactly: 51,792/7,006/1,353/2/1; "
    "validate green; F-0019 content-comparison heeded; replay ran clean on the first try). "
    "NO NEW TOOLING DEFECTS THIS SESSION. BATCH 7 REVIEW TRANCHE: 60 highest-signal "
    "unreviewed provisional candidates (4,814 matching the signal rule of 51,792 unreviewed; "
    "scripts/disc002_batch7_tranche.py, repo-relative, reads the replayed post-batch6 "
    "state). Tranche character: mixed — generic English vocabulary and prose fragments "
    "plus a technical minority (attention variants, DPO derivation, bfloat16, DeepSeek-R1, "
    "RAG ingestion, weight updates, CNN feature hierarchy, tuples, memory backends, audit "
    "logging, async/await). Method: individual evidence review of all 60 brief blocks + "
    "definitional-treatment coverage probe (scripts/disc002_batch7_probe.py, 58 terms) + "
    "targeted citation verification (scripts/disc002_batch7_verify.py, 58 locator checks, "
    "all OK after 3 fixes) + independent subagent cross-check of 27 judgment calls (15 "
    "covers + 1 confirm_gap + 1 merge + 10 borderline rejects): 27/27 AGREE; corrections "
    "incorporated (val citations upgraded from mermaid node labels :271/:667 to real "
    "headings :267/:368 with chapter-level parents — the mermaid-vs-heading confusion "
    "class struck again; ingestion citation upgraded from the worked-example step :420 to "
    "the definitional '### Indexing (offline, batch)' :54-60; deepseek-r1 cover "
    "strengthened with the dedicated paper note '26 - Papers/2024-2026/12 - DeepSeek-R1 "
    "2025.md'). DECISIONS: 15 evidence-cited covers (gqa mqa, gqa mqa mla, mqa mla, dpo "
    "derivation, bfloat16, deepseek-r1 2025, ingestion, weight updates, low-level "
    "features, tuple, pipeline overview, rag pipeline overview, memory backends, vector "
    "memory backends, audit log) + 1 NEW CONFIRMED GAP (async def — Python's async/await "
    "execution model used in implementation position in 17 master-ai files / 'await' in "
    "20, zero definitional treatment corpus-wide, ai-course Python curriculum contains "
    "ZERO async/await/asyncio/coroutine/event-loop occurrences; third confirmed gap "
    "overall after second moment and bradley-terry; destination: section in the "
    "Python-tooling/MCP-implementation treatment) + 1 merge (await -> async def "
    "CG-00366e34ee82) + 43 noise rejects "
    "(state/concept-candidates/002-disc002-decisions-batch7.jsonl; applied with "
    "--decided-utc 2026-10-31T00:30:00Z; reports/discovery/disc002-decide-batch7.json "
    "decisions_applied 1584 cumulative including the merge-absorb entry, "
    "disc002-validate-batch7.json 60,154 records 0 errors, disc002-index-batch7.json). "
    "POST-BATCH7: 51,732 provisional / 7,021 already_covered / 1,396 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged / 1 deferred; "
    "index delta-verified exactly (-60 provisional, +15 covered, +43 rejected, +1 "
    "confirmed_gap, +1 merged). REMAINING: batch-8+ review tranches (~4,754 still match "
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
st["stage"] = "disc002-review-batch7-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-31-disc002-session7.json"
st["notes"] = (
    "DISC-002 in progress; session 7 re-verified the baseline (663/663 tests at start, both "
    "vaults byte-identical to manifests at start and end), extended the ADR-0010 replay to "
    "seven decide rounds (content-identical to the committed index before the batch-7 "
    "apply; replay ran clean on the first try; no new tooling defects), and completed the "
    "batch-7 review tranche: 60 highest-signal unreviewed candidates (mixed generic + "
    "technical tranche), 58-term coverage probe + 58-check citation verification + "
    "independent subagent cross-check (27 judgment calls, 27/27 AGREE, corrections "
    "incorporated: mermaid-label citations replaced with real headings, ingestion citation "
    "upgraded, deepseek-r1 paper note added). Decisions: 15 evidence-cited covers + 1 NEW "
    "CONFIRMED GAP (async def: Python async/await used in 17 master-ai implementation "
    "files with zero definitional treatment corpus-wide — the ai-course Python curriculum "
    "never mentions async/await/asyncio/coroutine/event loop) + 1 merge (await -> async "
    "def) + 43 noise rejects applied (--decided-utc 2026-10-31T00:30:00Z), validate green, "
    "index regenerated and delta-verified. CURRENT: 51,732 provisional / 7,021 "
    "already_covered / 1,396 rejected / 3 confirmed_gap (second moment, bradley-terry, "
    "async def) / 1 merged / 1 deferred. NEXT: batch-8+ review tranches (~4,754 still "
    "match the signal rule); per-domain semantic classification of the dossier-extension "
    "overlap pairs (no bulk absorption); then disposition assignment before gated "
    "synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["confirmed_gaps"] = [
    "second moment",
    "bradley-terry",
    "async def",
]
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7021,
    "confirmed_gap": 3,
    "deferred": 1,
    "merged": 1,
    "provisional_candidate": 51732,
    "rejected": 1396,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch7.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch7"] = (
    "2026-10-31T00:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 7: seven-round replay re-verification + batch-7 tranche (15 covers + 1 new "
    "confirmed gap async def + 1 merge + 43 rejects)"
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
