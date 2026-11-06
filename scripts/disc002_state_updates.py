#!/usr/bin/env python3
"""DISC-002 session state updates: task queue progress note, checkpoint,
current-state.json, and handoff. Run AFTER the feat commit exists (the state
record references it); this script only rewrites state files, never sources.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FEAT_COMMIT = sys.argv[1] if len(sys.argv) > 1 else None
if not FEAT_COMMIT:
    FEAT_COMMIT = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()
    print(f"using HEAD as feat commit: {FEAT_COMMIT} (pass the real feat hash as argv[1] if different)")

# ---- 1. task queue: DISC-002 -> in_progress with progress note ----
queue_path = REPO / "state/task-queue.jsonl"
tasks = []
with open(queue_path, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            tasks.append(json.loads(line))
for t in tasks:
    if t["task_id"] == "DISC-002":
        t["status"] = "in_progress"
        t["notes"] = (
            "DISC-002 progress (feat commit " + FEAT_COMMIT[:7] + ", session of 2026-10-28): "
            "(1) corpus-scale hardening of discover-gaps + discovery-validate "
                    "(byte-identical output proven on the real 14-batch subset, "
                    "sha256 1322e74c; full run 547.4s, double-run byte-identical "
                    "88a538eb, peak RSS 1.95GB; validate O(n^2) dupe scan + "
                    "per-record schema re-check fixed, 60154 records in 37.7s). "
            "(2) full-corpus discovery run: 60154 candidates, 557504 terms, "
                    "coverage 276/276 + 333/333 COMPLETE (the hard gate is open). "
            "(3) deterministic triage (reports/discovery/disc002-triage.json): "
                    "T1 fragmented 1796, T2 broad-prereq 24068, T3 rare-essential "
                    "6512, T4 narrow 20922; 11839 n-gram-fragment flags. "
            "(4) review round 1 (class-based, independently verified by subagent, "
                    "0 hard false positives): 1153 rejects (R-NUM 793, R-CODE 360). "
            "(5) review round 2 (individual evidence review of the top tranche): "
                    "44 decisions — FIRST 2 CONFIRMED GAPS (second moment, "
                    "bradley-terry), 4 defers for family mapping, 7 covers "
                    "(paraphrased-definition false positives), 31 rejects. "
            "Remaining: 52101 provisional candidates need review tranches "
                    "(use scripts/disc002_review_brief.py + the class/family "
                    "strategy), deferred families (3d-tensor/shape, log-softmax/"
                    "numerical-stability, reference-policy, ssd-framework), "
                    "dossier extension (27 decisions touch dossier domains; "
                    "all 6 dossiers' KU refs verified intact), accepted-concept "
                    "flow into registry/dossiers. Candidates monolith is "
                    "git-ignored per ADR-0010; replay = discover-gaps then "
                    "discovery-decide r1+r2 with recorded --decided-utc."
        )
        t["tests_run"] = [
            "python3 -m pytest tests/ -q -> 620 passed (post-hardening, "
            "reports the suite evidence for feat commit " + FEAT_COMMIT[:7] + ")",
            "vu capabilities --verify -> 22 implemented-and-tested + 1 planned "
            "(reports/discovery/disc002-verify-capabilities.json)",
            "vu discovery-validate full-corpus candidates -> valid, 60154 records, "
            "0 errors (reports/discovery/disc002-validate.json, -post-r1, -post-r2)",
            "double-run byte-identical: sha256 88a538eb... both runs "
            "(reports/discovery/disc002-full-corpus-perf.json)",
        ]
with open(queue_path, "w", encoding="utf-8") as fh:
    for t in tasks:
        fh.write(json.dumps(t, sort_keys=True, ensure_ascii=False) + "\n")
print("task queue updated: DISC-002 -> in_progress with progress note")

# ---- 2. checkpoint ----
checkpoint = {
    "checkpoint_id": "checkpoint-2026-10-28-disc002-progress",
    "created_utc": "2026-10-28T02:20:00Z",
    "task_ids_completed": [
        "BOOT-000", "BOOT-001", "BOOT-002", "BOOT-003", "BOOT-004",
        "EXT-001", "EXT-002", "EXT-003", "EXT-004", "EXT-005", "EXT-006",
        "EXT-007", "EXT-008", "EXT-009", "EXT-010",
        "REBASE-000", "AUDIT-011", "FRAME-001", "DISC-001", "FRAME-002",
        "REGEN-001",
    ],
    "task_ids_open": ["DISC-002"],
    "task_ids_in_progress": ["DISC-002"],
    "framework_version": "0.8.0",
    "feat_commit": FEAT_COMMIT,
    "test_suite": {
        "command": "python3 -m pytest tests/ -q",
        "result": "620 passed (re-run after last mutation; see queue tests_run)",
    },
    "capabilities": {"verified": True, "implemented_and_tested": 22, "planned": 1},
    "discovery_state": {
        "coverage": "COMPLETE (276/276 ai-course + 333/333 master-ai)",
        "candidates_total": 60154,
        "by_status": {
            "provisional_candidate": 52101,
            "already_covered": 6863,
            "rejected": 1184,
            "confirmed_gap": 2,
            "deferred": 4,
        },
        "confirmed_gaps": ["second moment", "bradley-terry"],
        "candidates_file": "state/concept-candidates/002-disc002-full-corpus.jsonl (git-ignored, ADR-0010; regenerate via scripts/disc002_run_full.py then replay 002a+002b decisions)",
        "decisions_committed": [
            "state/concept-candidates/002a-disc002-decisions-r1.jsonl (1153 class-based rejects)",
            "state/concept-candidates/002b-disc002-decisions-r2.jsonl (44 individual decisions)",
        ],
    },
    "source_immutability": {
        "ai-course": "276/276 unchanged (manifest verify exit 0, session start)",
        "master-ai": "333/333 unchanged (manifest verify exit 0, session start)",
    },
    "next": [
        "continue DISC-002 review tranches (52,101 provisional remain): rerun "
        "scripts/disc002_review_brief.py, review T1/T2/T3 in domain batches, "
        "resolve the 4 deferred families, extend dossiers, then define the "
        "accepted-concept flow",
        "then disposition assignment (KU -> destination + disposition mapping) "
        "before gated synthesis",
    ],
}
cp_path = REPO / "state/checkpoints/checkpoint-2026-10-28-disc002-progress.json"
cp_path.write_text(json.dumps(checkpoint, indent=1) + "\n", encoding="utf-8")
print("checkpoint written:", cp_path.name)

# ---- 3. current-state.json ----
cs_path = REPO / "state/current-state.json"
cs = json.loads(cs_path.read_text(encoding="utf-8"))
cs["stage"] = "disc002-corpus-discovery-in-progress"
cs["current_task_id"] = "DISC-002"
cs["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-28-disc002-progress.json"
cs["notes"] = (
    "DISC-002 in progress (feat commit " + FEAT_COMMIT[:7] + ", 2026-10-28 session). "
    "Corpus-wide discovery COMPLETE and validated: 60,154 candidates over the full "
    "609-file corpus (coverage gate OPEN); double-run byte-identical (sha256 "
    "88a538eb); peak RSS 1.95GB; framework hardened for corpus scale with "
    "byte-identical-output proof (620/620 tests). Review rounds 1+2 applied: "
    "1,197 decisions (2 CONFIRMED GAPS: second moment, bradley-terry; 4 defers; "
    "7 covers; 1,184 rejects), 52,101 provisional candidates remain for review "
    "tranches. All six dossiers' KU references verified intact; 27 decisions "
    "touch dossier domains for the next extension pass. Candidates monolith "
    "git-ignored per ADR-0010 (replayable from committed batches + decisions). "
    "NEXT: continue review tranches via the brief/class/family strategy, extend "
    "dossiers, define accepted-concept flow, then disposition assignment before "
    "gated synthesis."
)
cs["phase_zero_rebaseline"]["discovery_full_corpus"] = {
    "task": "DISC-002 (in progress)",
    "candidates": 60154,
    "coverage_complete": True,
    "run_report": "reports/discovery/disc002-full-corpus-run.json",
    "perf": "reports/discovery/disc002-full-corpus-perf.json",
    "validate": "reports/discovery/disc002-validate.json",
    "triage": "reports/discovery/disc002-triage.json",
    "decide_r1": "reports/discovery/disc002-decide-r1.json",
    "decide_r2": "reports/discovery/disc002-decide-r2.json",
    "dossier_reconciliation": "reports/discovery/disc002-dossier-reconciliation.json",
    "tests": "620/620",
}
cs_path.write_text(json.dumps(cs, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print("current-state.json updated")
